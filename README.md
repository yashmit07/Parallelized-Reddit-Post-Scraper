# Parallelized Reddit Post Scraper

This project implements a parallelized Reddit post scraper that efficiently collects and analyzes posts from multiple subreddits using different parallelization techniques. The implementation compares three approaches: threading, multiprocessing, and distributed computing with Ray.

## Project Overview

The scraper is designed to:
- Fetch posts from multiple subreddits concurrently
- Compare performance between different execution methods
- Handle rate limiting and API restrictions gracefully
- Process and analyze post data efficiently
- Scale across distributed systems using Ray

## Implementation Details

The project implements three distinct approaches:
1. **Threading**: Using Python's threading for I/O-bound concurrent execution
2. **Multiprocessing**: Utilizing Python's multiprocessing for CPU-bound tasks
3. **Ray**: Distributed computing framework for scalable parallel processing

## Experimental Setup

Our experiments were conducted with the following parameters:
- Number of subreddits: 5 (programming, Python, learnpython, coding, compsci)
- Posts per subreddit: 100
- Total posts processed: 500
- Metrics measured: Execution time, CPU utilization, memory usage
- Ray cluster: Local machine with 4 worker processes

## Results and Findings

### Performance Comparison

1. **Threading Implementation**
   - Average execution time: ~8-10 seconds
   - CPU utilization: ~30%
   - Good performance for I/O-bound operations
   - ~2x speedup compared to sequential processing
   - Effective at handling concurrent API requests

2. **Multiprocessing Approach**
   - Average execution time: ~8-10 seconds
   - CPU utilization: ~80%
   - Significant improvement for CPU-bound tasks
   - ~2x speedup compared to sequential
   - Higher memory overhead due to process creation

3. **Ray Implementation**
   - Average execution time: ~6-8 seconds
   - CPU utilization: ~75%
   - Best overall performance
   - ~2.5x speedup compared to sequential
   - Efficient task distribution and resource management
   - Potential for scaling to multiple machines

### Performance Visualization

Below are the graphs comparing the performance metrics of our three implementations:

#### Execution Time Comparison
![Execution Time Comparison](images/execution_time_comparison.png)
*Figure 1: Average execution time comparison across different approaches. Lower is better.*

#### CPU Utilization Over Time
![CPU Utilization](images/cpu_utilization.png)
*Figure 2: CPU utilization patterns during execution. Ray and Multiprocessing show higher but more consistent CPU usage.*

#### Memory Usage Comparison
![Memory Usage](images/memory_usage.png)
*Figure 3: Memory footprint comparison. Threading shows the lowest memory usage while Ray maintains a balanced profile.*

#### Scalability Test Results
![Scalability Test](images/scalability_test.png)
*Figure 4: Performance scaling with increasing number of subreddits. Ray shows the best scaling characteristics.*

### Key Findings

1. **Ray Superiority**: The Ray implementation proved most efficient for our use case, combining the benefits of both threading and multiprocessing with additional distributed computing capabilities.
2. **Resource Utilization**: Multiprocessing showed higher CPU usage but similar performance to threading due to the I/O-bound nature of the task.
3. **Memory Usage**: Threading maintained the lowest memory footprint while Ray provided the best balance between resource usage and performance.
4. **Rate Limiting**: All implementations successfully handled Reddit's rate limiting, with Ray managing it most effectively through its built-in scheduling and resource management.
5. **Scalability**: Ray demonstrated the best potential for scaling, as it can easily extend to multiple machines without code changes.

## Setup and Usage

### Prerequisites
- Python 3.7+
- PRAW (Python Reddit API Wrapper)
- threading (built-in)
- multiprocessing (built-in)
- ray

### Installation
1. Clone the repository:
```bash
git clone https://github.com/yourusername/Parallelized-Reddit-Post-Scraper.git
cd Parallelized-Reddit-Post-Scraper
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Configure Reddit API credentials:
- Create a Reddit application at https://www.reddit.com/prefs/apps
- Copy `config_template.py` to `config.py`
- Fill in your Reddit API credentials in `config.py`

### Running the Scraper
```bash
python main.py --mode [threading|multiprocessing|ray] --subreddits [subreddit1,subreddit2,...] --posts_per_subreddit [number]
```

## Conclusions

Our experiments demonstrate that for Reddit post scraping:
1. Ray provides the best overall performance with built-in distributed capabilities
2. Threading is effective for I/O-bound operations with minimal overhead
3. Multiprocessing offers good CPU utilization but with higher resource overhead
4. The choice of parallelization method should match the workload type and scaling requirements

The project successfully achieved its goal of optimizing Reddit post collection through parallelization. Ray emerged as the most efficient and scalable solution, while threading and multiprocessing each showed specific advantages for different aspects of the task. 
