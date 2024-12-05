package main

import (
	"encoding/json"
	"fmt"
	"io/ioutil"
	"log"
	"net/http"
	"os"
	"regexp"
)

// APIResponse represents the structure of the JSON response
type APIResponse struct {
	ResponseMap []ResponseMap `json:"response_map"`
}

// ResponseMap represents each response map entry
type ResponseMap struct {
	Running []RunningItem `json:"running"`
}

// RunningItem holds the running array items
type RunningItem struct {
	Label    string  `json:"label"`
	Hostname string  `json:"hostname"`
	Location string  `json:"location"`
	InfoMap  InfoMap `json:"info_map"`
}

// InfoMap holds additional metadata
type InfoMap struct {
	Ports []PortEntry `json:"ports"`
}

// PortEntry holds port details
type PortEntry struct {
	Name string `json:"name"`
	Port string `json:"port"`
}

// TargetConfig represents the structure of the JSON to be saved
type TargetConfig struct {
	Targets []string          `json:"targets"`
	Labels  map[string]string `json:"labels"`
}

// fetchAPIResponse fetches the API response with Basic Authentication
func fetchAPIResponse(apiURL, username, password string) ([]byte, error) {
	log.Printf("Fetching API response from URL: %s", apiURL)

	client := &http.Client{}
	req, err := http.NewRequest("GET", apiURL, nil)
	if err != nil {
		log.Printf("Error creating request: %v", err)
		return nil, err
	}

	req.SetBasicAuth(username, password)
	log.Println("Request created with Basic Auth.")

	resp, err := client.Do(req)
	if err != nil {
		log.Printf("Error making request: %v", err)
		return nil, err
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK {
		log.Printf("Failed to fetch data, status: %s", resp.Status)
		return nil, fmt.Errorf("failed to fetch data: %s", resp.Status)
	}

	log.Println("Successfully fetched API response.")
	return ioutil.ReadAll(resp.Body)
}

// parseRunningArray parses the running array and constructs the target configurations
func parseRunningArray(data []byte) ([]TargetConfig, error) {
	log.Println("Parsing running array from API response.")

	var apiResponse APIResponse
	err := json.Unmarshal(data, &apiResponse)
	if err != nil {
		log.Printf("Error unmarshalling JSON response: %v", err)
		return nil, err
	}

	var targetConfigs []TargetConfig
	labelRegex := regexp.MustCompile(`ip-(\d+)-(\d+)-(\d+)-(\d+)`)

	for _, respMap := range apiResponse.ResponseMap {
		for _, running := range respMap.Running {
			log.Printf("Processing running item: %v", running)

			// Determine IP source based on location
			source := running.Label
			if running.Location == "cloud" {
				source = running.Hostname
			} else {
				matches := labelRegex.FindStringSubmatch(running.Label)

				if len(matches) == 5 {
					source = fmt.Sprintf("%s.%s.%s.%s", matches[1], matches[2], matches[3], matches[4])
				}
			}

			// Find secure port
			var securePort string
			for _, port := range running.InfoMap.Ports {
				if port.Name == "cc_secure_port" {
					securePort = port.Port
					break
				}
			}

			log.Printf("Source: %s, Secure Port: %s", source, securePort)

			if securePort != "" {
				targetConfig := TargetConfig{
					Targets: []string{fmt.Sprintf("%s:%s", source, securePort)},
					Labels: map[string]string{
						"labelname": source,
					},
				}
				targetConfigs = append(targetConfigs, targetConfig)
				log.Printf("TargetConfig added: %v", targetConfig)
			}
		}
	}

	log.Printf("Finished parsing running array. Total TargetConfigs: %d", len(targetConfigs))
	return targetConfigs, nil
}

// saveToFile saves the results to a file in JSON format
func saveToFile(targetConfigs []TargetConfig, filePath string) error {
	log.Printf("Saving target configurations to file: %s", filePath)

	content, err := json.MarshalIndent(targetConfigs, "", "  ")
	if err != nil {
		log.Printf("Error marshalling target configurations to JSON: %v", err)
		return err
	}

	err = ioutil.WriteFile(filePath, content, 0644)
	if err != nil {
		log.Printf("Error writing to file: %v", err)
		return err
	}

	log.Println("File saved successfully.")
	return nil
}

func main() {
	log.Println("Starting the Go application.")

	apiURL := os.Getenv("API_URL")
	username := os.Getenv("API_USERNAME")
	password := os.Getenv("API_PASSWORD")
	outputFilePath := "targets.json"

	if apiURL == "" || username == "" || password == "" {
		log.Fatalf("Environment variables API_URL, API_USERNAME, and API_PASSWORD must be set")
	}

	log.Println("Fetching API response...")
	data, err := fetchAPIResponse(apiURL, username, password)
	if err != nil {
		log.Fatalf("Error fetching API response: %v", err)
	}

	log.Println("Parsing running array...")
	targetConfigs, err := parseRunningArray(data)
	if err != nil {
		log.Fatalf("Error parsing running array: %v", err)
	}

	log.Println("Saving results to file...")
	err = saveToFile(targetConfigs, outputFilePath)
	if err != nil {
		log.Fatalf("Error saving results to file: %v", err)
	}

	log.Printf("Target configurations saved to %s", outputFilePath)
	log.Println("Go application finished successfully.")
}
