import csv
import recurring_content_detector as rcd

SHOW_NAME="DunkLeague"
#COLUMNS = ['filename' , 'recap_start', 'recap_end', 'openingcredits_start', 'openingcredits_end', 'preview_start', 'preview_end', 'closingcredits_start', 'closingcredits_end']
COLUMNS = ['filename']

results = rcd.detect("videos", artifacts_dir= "artifacts", resize_width=720, percentile=5, video_start_threshold_percentile=10, min_detection_size_seconds=5, video_end_threshold_seconds=15)

with open('/opt/recurring-content-detector/scripts/{}.csv'.format(SHOW_NAME), mode='w') as csvfile:
    writer = csv.writer(csvfile, delimiter=',',
                  quotechar='|', quoting=csv.QUOTE_MINIMAL)
    writer.writerow(COLUMNS)
    for video_name, detections in results.items():
        start_times = []
        start_times.append(video_name)
        for d in detections:
            print("Writing: {}".format(rcd.to_time_string(d[0])))
            start_times.append("{}-{}".format(rcd.to_time_string(d[0]), rcd.to_time_string(d[1])))
        writer.writerow(start_times)
    

print(results)
print(type(results))
