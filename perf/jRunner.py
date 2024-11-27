import os
import subprocess
import argparse
from datetime import datetime


# args: jmx_file, root_dir
def search_jmx(jmx_file_name, root_dir='/'):
    print(f"Searching for given file: {jmx_file_name}")
    matching_file = []
    current_directory = os.getcwd()
    search_dirs = [current_directory] if root_dir == '/' else [current_directory, root_dir]
    for base_dir in search_dirs:
        for walk_dir, dir_names, file_names in os.walk(base_dir):
            for name in file_names:
                if jmx_file_name.lower() in name.lower():
                    matching_file.append(os.path.join(walk_dir, name))
    return matching_file


def run_jmeter(file_path, threads, ramp_up, loop_count, report_file, base_url, jmeter_path="jmeter"):
    # Remove test report file if it already exists
    if os.path.exists(report_file):
        os.remove(report_file)
        print(f"Existing report file '{report_file}' removed.")

    """
    Usage example:
    python3 jrunner.py -f RTTChildToGrandChild.jmx -t 16 canv2-dpperf-groundsnaplexmedium-fm.snaplogicdev.io
    jmeter -n -t RTTChildToGrandChild.jmx -l results.csv -JTHREADS=16 -JBASE_URL=canv2-dpperf-groundsnaplexmedium-fm.snaplogicdev.io
    """

    # Construct the JMeter command to run
    command = [
        jmeter_path,
        "-n",                                 # Run in non-GUI mode
        "-t", file_path,                      # JMX test file
        "-JTHREADS={}".format(threads),       # Number of threads
        "-Jrampup={}".format(ramp_up),        # Ramp-up period
        "-Jloopcount={}".format(loop_count),  # Loop count
        "-JBASE_URL={}".format(base_url),     # Environment URL
        "-l", report_file,                    # Output results file
        "-f"                                  # Force to delete the results
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


if __name__ == "__main__":
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description="Run JMeter test plans with specified parameters.")
    parser.add_argument("-f", "--file", required=True, help="Path to the JMX test plan file")
    parser.add_argument("-t", "--threads", type=int, required=True, help="Number of concurrent users (threads)")
    parser.add_argument("base_url", help="Base URL for the environment under test (positional argument)")
    parser.add_argument("-r", "--rampup", type=int, default=1, help="Ramp-up time in seconds (default: 1)")
    parser.add_argument("-l", "--loopcount", type=int, default=1, help="Loop count (default: 1)")
    parser.add_argument("-o", "--output",
                        help="Path to the output results file (optional, defaults to a timestamped filename)")
    parser.add_argument("-p", "--jmeterpath", default="jmeter", help="Path to the JMeter executable")

    args = parser.parse_args()

    # If a file path was provided in args.file, just use it.
    jmx_file = args.file

    # If no file is found, attempt to search for it in the specified directory
    if not os.path.exists(jmx_file):
        print(f"File '{jmx_file}' not found in the specified path. Attempting to search...")
        matching_files = search_jmx(jmx_file, '/data-plane')  # Adjust search root if needed

        if not matching_files:
            print("File not found in the search path.")
            exit(1)
        else:
            print(f"File found at: {matching_files[0]}")
            jmx_file = matching_files[0]

    # Generate csv report
    if not args.output:
        timestamp = datetime.now().strftime("%b-%d-%I-%M%p").lower()
        args.output = f"results/{timestamp}-pst-{args.threads}-threads.csv"

    print(f"Performance results file: {args.output}")

    # Run JMeter with parsed arguments
    run_jmeter(
        file_path=jmx_file,
        threads=args.threads,
        ramp_up=args.rampup,
        loop_count=args.loopcount,
        report_file=args.output,
        base_url=args.base_url,
        jmeter_path=args.jmeterpath
    )
