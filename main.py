import os
import pandas as pd
import json
import matplotlib.pyplot as plt
import yaml
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def show_viz(df: pd.DataFrame, start_date: str, end_date: str) -> None:
    df['timestamp'] = pd.to_datetime(df['timestamp'], format='mixed')
    df['date'] = df['timestamp'].dt.date
    df['year_month'] = df['timestamp'].dt.strftime('%Y-%m')

    df_filtered = df[df['status'] > 299]
    grouped = df_filtered.groupby(['year_month', 'status']).size().reset_index(name='count')
    pivoted = grouped.pivot(index='year_month', columns='status', values='count').fillna(0)
    # Ensure the index is sorted by date
    pivoted = pivoted.sort_index()

    # Plot the requests with http status > 299
    pivoted.plot(kind='bar', stacked=True, figsize=(10, 6))
    plt.xlabel('Date')
    plt.ylabel('Count')
    plt.title('HTTP Status Counts Per Month')
    plt.legend(title='HTTP Status')
    plt.xticks(rotation=45)
    plt.show()

    # Filter the DataFrame by the date range
    filtered_df = df[(df['timestamp'] >= start_date) & (df['timestamp'] < end_date)]

    # Count the occurrences of each endpoint in the filtered DataFrame
    endpoint_counts = filtered_df['endpoint'].value_counts()

    # Plot the total rows per endpoint
    plt.figure(figsize=(10, 6))
    endpoint_counts.plot(kind='barh')
    plt.xlabel('Endpoint')
    plt.ylabel('Total Requests')
    plt.title(f'Total Requests per Endpoint (start:{start_date}, end: {end_date})')
    plt.show()


def process_json_files(root_dir: str) -> pd.DataFrame:
    file_count = 0
    requests = []
    for root, dirs, files in os.walk(root_dir):
        for file in files:
            if file.endswith('.json'):
                file_name = os.path.join(root, file)
                try:
                    with open(file_name, 'r') as file:
                        for line in file:
                            record = json.loads(line.strip())
                            # print(f"processing record: {record}")
                            if record.get('method') == 'GET':
                                view_args_id = 'Not found'
                                if record.get('view-args', {}) is not None:
                                    if record.get('view-args', {}).get('id') is not None:
                                        view_args_id = record.get('view-args', {}).get('id')

                                requests.append({
                                    'endpoint': record.get('endpoint'),
                                    'view-args.id': view_args_id,
                                    'user': record.get('user'),
                                    'timestamp': record.get('timestamp'),
                                    'status': record.get('status'),
                                    'browser': record.get('browser'),
                                    'browser-platform': record.get('browser-platform'),
                                    'browser-version': record.get('browser-version')
                                })
                    file_count += 1
                except json.JSONDecodeError:
                    logging.error(f"Error decoding JSON in file: {file_name}")
                except Exception as e:
                    logging.error(f"Unexpected error processing file {file_name}: {e}")

    logging.info(f"Processed files: {file_count}")
    df = pd.DataFrame(requests)
    return df


def data_export(df: pd.DataFrame, file_name: str, exp_start_date: str, exp_end_date: str) -> None:
    filtered_df = df[(df['timestamp'] >= exp_start_date) & (df['timestamp'] < exp_end_date)]

    # Group by 'endpoint' and 'date', then count the occurrences
    daily_rate = filtered_df.groupby(['endpoint', filtered_df['date']]).size().reset_index(name='count')

    daily_rate.to_csv(file_name)
    print(f"data exported to file: {file_name}, start_date:{exp_start_date}, end_date: {exp_end_date}")


if __name__ == "__main__":
    env = 'prod'
    try:
        # get configuration parameters
        config = yaml.safe_load(open("config.yml"))

        # process json files
        requests_folder = config[env]['requests_file_path']
        processed_files = process_json_files(requests_folder)

        # show visualizations
        start_date = config['viz']['start_date']
        end_date = config['viz']['end_date']
        show_viz(processed_files, start_date, end_date)

        # export data to csv
        export_file_name = config['export']['export_file_name']
        start_date = config['export']['start_date']
        end_date = config['export']['end_date']
        data_export(processed_files, export_file_name, start_date, end_date)
    except Exception as e:
        logging.error(f"An error occurred: {e}")

