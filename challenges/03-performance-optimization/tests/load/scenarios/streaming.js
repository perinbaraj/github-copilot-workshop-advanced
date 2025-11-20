import http from 'k6/http';
import { check, sleep } from 'k6';

export let options = {
  scenarios: {
    video_streaming: {
      executor: 'constant-vus',
      vus: 100,
      duration: '2m',
    },
  },
  thresholds: {
    http_req_duration: ['p(95)<1000'],
    http_req_failed: ['rate<0.05'],
  },
};

const BASE_URL = __ENV.BASE_URL || 'http://localhost:3000';

export default function () {
  // Random video ID
  const videoId = Math.floor(Math.random() * 1000) + 1;
  
  // Get video details
  let res = http.get(`${BASE_URL}/api/videos/${videoId}`);
  check(res, {
    'video detail loaded': (r) => r.status === 200,
  });
  
  sleep(1);
  
  // Simulate watching video (increment view)
  res = http.post(`${BASE_URL}/api/videos/${videoId}/view`, null);
  check(res, {
    'view recorded': (r) => r.status === 200 || r.status === 201,
  });
  
  // Simulate watching for 30-300 seconds
  const watchTime = Math.floor(Math.random() * 270) + 30;
  sleep(watchTime / 10); // Compressed time for testing
  
  // Get comments
  res = http.get(`${BASE_URL}/api/videos/${videoId}/comments?page=1&limit=50`);
  check(res, {
    'comments loaded': (r) => r.status === 200,
  });
  
  sleep(2);
}
