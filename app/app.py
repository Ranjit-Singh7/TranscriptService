from flask import Flask, request, jsonify
from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled, NoTranscriptFound, VideoUnavailable
import json

app = Flask(__name__)

def merge_json(transcript):
  merged = []
  current_text = ''
  current_start = 0
  current_duration = 0
  for m1 in transcript:
    if len(current_text) > 500:
      merged.append({
          'text':current_text,
          'start':current_start,
          'duration':current_duration
      })
      current_text = m1['text']
      current_start = m1['start']
      current_duration = m1['duration']
    else:
      current_duration+=m1['duration']
      current_text+=m1['text']
  if len(current_text):
      current_text = m1['text']
      current_start = m1['start']
      current_duration = m1['duration']
  return merged


def club_json_texts(json_array):
    max_words = 50
    result = []
    current_combined_text = ""
    current_duration = 0
    current_start = json_array[0]['start']

    for entry in json_array:
        new_text = entry['text']
        new_duration = entry['duration']
        new_start = entry['start']

        combined_text = current_combined_text + " " + new_text if current_combined_text else new_text
        word_count = len(combined_text.split())

        if word_count <= max_words:
            current_combined_text = combined_text
            current_duration += new_duration
        else:
            result.append({
                "duration": current_duration,
                "start": current_start,
                "text": current_combined_text
            })
            current_combined_text = new_text
            current_duration = new_duration
            current_start = new_start

    if current_combined_text:
        result.append({
            "duration": current_duration,
            "start": current_start,
            "text": current_combined_text
        })

    return result


@app.route('/get_transcript', methods=['GET'])
def get_transcript():
    video_id = request.args.get('video_id')

    if not video_id:
        return jsonify({"error": "Missing video_id parameter"}), 400

    try:
        transcript = YouTubeTranscriptApi.get_transcript(video_id)
        output_json = club_json_texts(transcript)
        return jsonify(output_json), 200
    except TranscriptsDisabled:
        return jsonify({"error": "Transcripts are disabled for this video"}), 403
    except NoTranscriptFound:
        return jsonify({"error": "No transcript found for this video"}), 404
    except VideoUnavailable:
        return jsonify({"error": "Video is unavailable"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)


