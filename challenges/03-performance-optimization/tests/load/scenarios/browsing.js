import http from 'k6/http';
import { check, sleep } from 'k6';

export let options = {
  stages: [
    { duration: '30s', target: 20 },  // Ramp up to 20 users
    { duration: '1m', target: 50 },   // Ramp up to 50 users
    { duration: '2m', target: 100 },  // Ramp up to 100 users
    { duration: '1m', target: 0 },    // Ramp down
  ],
  thresholds: {
    http_req_duration: ['p(95)<500'], // 95% of requests should be below 500ms
    http_req_failed: ['rate<0.01'],   // Less than 1% errors
  },
};

const BASE_URL = __ENV.BASE_URL || 'http://localhost:3000';

export default function () {
  // Scenario 1: Browse homepage
  let res = http.get(`${BASE_URL}/api/videos?page=1&limit=20`);
  check(res, {
    'homepage status is 200': (r) => r.status === 200,
    'homepage response time < 500ms': (r) => r.timings.duration < 500,
  });
  
  sleep(1);
  
  // Scenario 2: View video details
  const videoId = Math.floor(Math.random() * 1000) + 1;
  res = http.get(`${BASE_URL}/api/videos/${videoId}`);
  check(res, {
    'video detail status is 200': (r) => r.status === 200,
    'video detail response time < 300ms': (r) => r.timings.duration < 300,
  });
  
  sleep(2);
  
  // Scenario 3: Search videos
  const searchTerms = ['gaming', 'music', 'tutorial', 'tech', 'review'];
  const searchTerm = searchTerms[Math.floor(Math.random() * searchTerms.length)];
  res = http.get(`${BASE_URL}/api/search?q=${searchTerm}`);
  check(res, {
    'search status is 200': (r) => r.status === 200,
    'search response time < 200ms': (r) => r.timings.duration < 200,
  });
  
  sleep(1);
  
  // Scenario 4: Get trending videos
  res = http.get(`${BASE_URL}/api/trending`);
  check(res, {
    'trending status is 200': (r) => r.status === 200,
    'trending response time < 300ms': (r) => r.timings.duration < 300,
  });
  
  sleep(2);
}
