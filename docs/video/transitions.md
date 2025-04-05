# Video Transitions Endpoint

## 1. Overview

The `/v1/video/transitions` endpoint is part of the Video API and allows users to apply transition effects between multiple video files. This endpoint provides a simple way to create seamless transitions between videos, such as fades, dissolves, and wipes. The processed video with transitions is uploaded to cloud storage, and the URL is returned in the response.

## 2. Endpoint Information

**URL Path:** `/v1/video/transitions`

**Method:** POST

**Authentication Required:** Yes

## 3. Request Parameters

| Parameter    | Type   | Required | Description                                                  |
|--------------|--------|----------|--------------------------------------------------------------|
| `videos`     | array  | Yes      | Array of video objects, each containing a video_url          |
| `transition` | string | Yes      | The type of transition to apply (see supported transitions)  |
| `params`     | object | No       | Additional parameters specific to the selected transition    |
| `webhook_url`| string | No       | URL to receive processing notifications                      |
| `id`         | string | No       | Custom identifier for the request                            |

### Supported Transitions

- **fade**: Creates a fade out/fade in transition between videos
  - Parameters: `duration` (number, default: 1.0) - Duration of the transition in seconds

- **dissolve**: Creates a crossfade/dissolve effect between videos
  - Parameters: `duration` (number, default: 1.0) - Duration of the transition in seconds

- **wipe**: Creates a wipe transition effect between videos
  - Parameters: 
    - `duration` (number, default: 1.0) - Duration of the transition in seconds
    - `direction` (string, default: "left") - Direction of the wipe ("left", "right", "up", or "down")

## 4. Request Example

```json
{
  "videos": [
    {"video_url": "https://example.com/video1.mp4"},
    {"video_url": "https://example.com/video2.mp4"},
    {"video_url": "https://example.com/video3.mp4"}
  ],
  "transition": "dissolve",
  "params": {
    "duration": 1.5
  },
  "webhook_url": "https://your-webhook.com/callback",
  "id": "custom-request-id"
}
```

## 5. Response

### Success Response (200 OK)

```json
{
  "code": 200,
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "id": "custom-request-id",
  "response": {
    "file_url": "https://cloud-storage.example.com/processed-video.mp4"
  },
  "message": "success",
  "run_time": 8.234,
  "queue_time": 0.123,
  "total_time": 8.357,
  "pid": 12345,
  "queue_id": 67890,
  "queue_length": 0,
  "build_number": "1.0.123"
}
```

### Error Response (500 Internal Server Error)

```json
{
  "code": 500,
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "id": "custom-request-id",
  "message": "Error processing video transitions: Invalid video format",
  "run_time": 0.234,
  "queue_time": 0.123,
  "total_time": 0.357,
  "pid": 12345,
  "queue_id": 67890,
  "queue_length": 0,
  "build_number": "1.0.123"
}
```

## 6. Usage Notes

- The maximum supported video size and duration may be limited by the server configuration.
- For best results, ensure that all videos have similar resolutions and aspect ratios.
- Transition duration should be appropriate for the content - typically 0.5 to 2 seconds works well.
- When using multiple videos (more than 2), the same transition type and parameters will be applied between each consecutive pair of videos.
- Processing time increases with the number of videos and the complexity of the transitions.

## 7. Common Errors

- **Invalid video URL**: Ensure all video URLs are accessible and point to valid video files.
- **Unsupported video format**: The API supports common video formats like MP4, MOV, AVI, etc.
- **Invalid transition parameters**: Ensure the parameters are within the allowed ranges.
- **Incompatible videos**: Videos with vastly different resolutions or codecs may cause issues.

## 8. Best Practices

- Use the webhook URL for asynchronous processing, especially when combining multiple videos.
- Test transitions with short video clips before processing longer content.
- For complex projects with many transitions, consider breaking the process into smaller batches.
- Ensure videos have similar audio levels to avoid jarring audio transitions.
- For precise control over transitions, consider using the FFmpeg compose endpoint.