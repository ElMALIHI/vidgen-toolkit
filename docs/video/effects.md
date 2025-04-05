# Video Effects Endpoint

## 1. Overview

The `/v1/video/effects` endpoint is part of the Video API and allows users to apply various visual effects to video files. This endpoint provides a simple way to enhance videos with effects like blur, sharpen, grayscale, sepia, and more. The processed video is uploaded to cloud storage, and the URL is returned in the response.

## 2. Endpoint Information

**URL Path:** `/v1/video/effects`

**Method:** POST

**Authentication Required:** Yes

## 3. Request Parameters

| Parameter  | Type   | Required | Description                                                  |
|------------|--------|----------|--------------------------------------------------------------|
| `video_url`| string | Yes      | The URL of the video file to process                         |
| `effect`   | string | Yes      | The type of effect to apply (see supported effects below)    |
| `params`   | object | No       | Additional parameters specific to the selected effect        |
| `webhook_url` | string | No    | URL to receive processing notifications                      |
| `id`       | string | No       | Custom identifier for the request                            |

### Supported Effects

- **blur**: Applies a blur effect to the video
  - Parameters: `amount` (number, default: 5) - Controls the blur intensity

- **sharpen**: Enhances the sharpness of the video
  - Parameters: `amount` (number, default: 5) - Controls the sharpening intensity

- **grayscale**: Converts the video to black and white
  - No additional parameters

- **sepia**: Applies a vintage sepia tone effect
  - No additional parameters

- **vignette**: Adds a vignette (darkened edges) to the video
  - Parameters: `amount` (number, default: 0.3) - Controls the vignette intensity

- **mirror**: Flips the video horizontally or vertically
  - Parameters: `direction` (string, default: "horizontal") - Either "horizontal" or "vertical"

- **rotate**: Rotates the video by a specified angle
  - Parameters: `angle` (number, default: 90) - Rotation angle in degrees

- **speed**: Changes the playback speed of the video
  - Parameters: `factor` (number, default: 2.0) - Speed factor (0.5 = half speed, 2.0 = double speed)

- **reverse**: Plays the video in reverse
  - No additional parameters

## 4. Request Example

```json
{
  "video_url": "https://example.com/video.mp4",
  "effect": "blur",
  "params": {
    "amount": 10
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
  "run_time": 5.234,
  "queue_time": 0.123,
  "total_time": 5.357,
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
  "message": "Error processing video effect: Invalid video format",
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
- Some effects may increase processing time significantly for large videos.
- For the `speed` effect, values between 0.5 and 2.0 generally produce the best results.
- When using the `rotate` effect, consider that the output dimensions may change.
- The processed video maintains the original resolution and quality unless the effect inherently changes these properties.

## 7. Common Errors

- **Invalid video URL**: Ensure the video URL is accessible and points to a valid video file.
- **Unsupported video format**: The API supports common video formats like MP4, MOV, AVI, etc.
- **Invalid effect parameters**: Ensure the parameters are within the allowed ranges.

## 8. Best Practices

- Use the webhook URL for asynchronous processing of large videos.
- Test effects with short video clips before processing longer content.
- Consider the impact of effects on video file size and quality.
- For complex effect chains, consider using multiple API calls or the FFmpeg compose endpoint.