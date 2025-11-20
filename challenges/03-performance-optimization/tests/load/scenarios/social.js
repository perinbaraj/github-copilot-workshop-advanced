import http from 'k6/http';
import { check, sleep } from 'k6';

export let options = {
  scenarios: {
    social_interactions: {
      executor: 'ramping-arrival-rate',
      startRate: 10,
      timeUnit: '1s',
      preAllocatedVUs: 50,
      maxVUs: 200,
      stages: [
        { target: 50, duration: '1m' },
        { target: 100, duration: '2m' },
        { target: 50, duration: '1m' },
      ],
    },
  },
};

const BASE_URL = __ENV.BASE_URL || 'http://localhost:3000';

export default function () {
  const videoId = Math.floor(Math.random() * 1000) + 1;
  const userId = Math.floor(Math.random() * 100) + 1;
  
  // Like a video
  let res = http.post(`${BASE_URL}/api/videos/${videoId}/like`, 
    JSON.stringify({ user_id: userId }),
    { headers: { 'Content-Type': 'application/json' } }
  );
  check(res, {
    'like registered': (r) => r.status === 200 || r.status === 201,
  });
  
  sleep(1);
  
  // Post a comment
  res = http.post(`${BASE_URL}/api/videos/${videoId}/comments`,
    JSON.stringify({
      user_id: userId,
      content: `Great video! Comment ${Date.now()}`
    }),
    { headers: { 'Content-Type': 'application/json' } }
  );
  check(res, {
    'comment posted': (r) => r.status === 200 || r.status === 201,
  });
  
  sleep(2);
  
  // Get user feed
  res = http.get(`${BASE_URL}/api/feed?user_id=${userId}&page=1&limit=20`);
  check(res, {
    'feed loaded': (r) => r.status === 200,
    'feed response time < 1s': (r) => r.timings.duration < 1000,
  });
  
  sleep(3);
}
