This repository contains the jmeter test scripts and configurations used by the Data Plane team for performance load testing for QA activities. 

### Prerequisites
Before you can run the JMeter, make sure that you have following
- Java 8+ t
- Apache JMeter installed on your machine. You can download it from https://jmeter.apache.org/download_jmeter.cgi.
- Python3 to run jmx files from commandline (enhanced command line expirience)

- To verify installation
```
java -version
python3 -version
jmeter -v
```

### Getting Started

Clone the Repository

To start using the test scripts, clone this repository to your local machine:
```
git clone https://github.com/SnapLogic/DataPlanePerf.git
```

## Launch JMeter
Once everything is set up, you can launch JMeter using the following command:
```
jmeter -open
```


## Directory Structure

```
DataPlanePerf/
├── jenkins/              # Jenkins support files
├── perf/                 # JMeter scripts (*.jmx files)
└── README.md             # Project overview and instructions
```


## Running the Tests

### Using the JMeter GUI:
* Open JMeter jmeter -open
* Load the desired .jmx test plan

### Using the JMeter command line
```
jmeter -n -t RTTChildToGrandChild.jmx -l results.csv -JTHREADS=16 -JBASE_URL=canv2-dpperf-groundsnaplexmedium-fm.snaplogicdev.io
```


## Contributing
QA GitHub PR flow

https://mysnaplogic.atlassian.net/wiki/spaces/QA/pages/3254747205/QA+GitHub+PR+flow

if any questions, reach out either #data_plane_qa #dp-qa-alerts slack channel