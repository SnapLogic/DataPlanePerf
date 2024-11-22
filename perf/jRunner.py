import os
import subprocess
import argparse
from datetime import datetime

# parse based on the size
# pre setup with endpoint to get the snaplex 


def run_jmeter(jmx_file, threads, ramp_up, loop_count, report_file, jmeter_path="jmeter"):
    # Remove report file if it already exists
    if os.path.exists(report_file):
        os.remove(report_file)
        print(f"Existing report file '{report_file}' removed.")

    """
    Usage example:
    python3 jrunner.py -f RTTChildToGrandChild.jmx -t 16
    jmeter -n -t RTTChildToGrandChild.jmx -l results.csv -JTHREADS=16

    """    
    
    # Construct the JMeter command to run
    command = [
        jmeter_path,
        "-n",                                 # Run in non-GUI mode
        "-t", jmx_file,                       # JMX test file
        "-JTHREADS={}".format(threads),       # Number of threads
        "-Jrampup={}".format(ramp_up),        # Ramp-up period
        "-Jloopcount={}".format(loop_count),  # Loop count
        "-l", report_file                     # Output results file
    ]
    
    print("Running JMeter with the following command:")
    print(" ".join(command))
    
    # Run the command and capture output
    try:
        result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
        print("JMeter test executed successfully!")
        print(result.stdout.decode())
        return result.stdout.decode()
    except subprocess.CalledProcessError as e:
        print("JMeter test failed.")
        print(e.stderr.decode())
        return None

    # parse the csv file
    #for i in range():
    #    report_file = 

    # elapsed is elapsed time must be the longest value from the list
    # label is Test Scenario name
    # success is for assertion, need to calculate the percentage for report
    # Release version is a function that needs to be called via curl to get jcc version. 
        
if __name__ == "__main__":
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description="Run JMeter test plans with specified parameters.")
    parser.add_argument("-f", "--file", required=True, help="Path to the JMX test plan file")
    parser.add_argument("-t", "--threads", type=int, required=True, help="Number of concurrent users (threads)")
    parser.add_argument("-r", "--rampup", type=int, default=1, help="Ramp-up time in seconds (default: 1)")
    parser.add_argument("-l", "--loopcount", type=int, default=1, help="Loop count (default: 1)")
    parser.add_argument("-o", "--output", help="Path to the output results file (optional, defaults to a timestamped filename)")
    parser.add_argument("-p", "--jmeterpath", default="jmeter", help="Path to the JMeter executable (default: jmeter)")

    args = parser.parse_args()

    # Generate csv report
    if not args.output:
        timestamp = datetime.now().strftime("%b-%d-%I-%M%p").lower()
        args.output = f"{timestamp}-pst-{args.threads}-threads.csv"

    print(f"Performance results file: {args.output}")

    # Run JMeter with parsed arguments
    run_jmeter(
        jmx_file=args.file,
        threads=args.threads,
        ramp_up=args.rampup,
        loop_count=args.loopcount,
        report_file=args.output,
        jmeter_path=args.jmeterpath
    )