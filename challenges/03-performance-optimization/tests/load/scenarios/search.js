import http from 'k6/http';
import { check, sleep } from 'k6';

export let options = {
  scenarios: {
    search_load: {
      executor: 'ramping-vus',
      startVUs: 0,
      stages: [
        { duration: '30s', target: 50 },
        { duration: '1m', target: 100 },
        { duration: '30s', target: 0 },
      ],
    },
  },
  thresholds: {
    http_req_duration: ['p(95)<200'],
    http_req_failed: ['rate<0.01'],
  },
};

const BASE_URL = __ENV.BASE_URL || 'http://localhost:3000';

const searchQueries = [
  'react tutorial',
  'nodejs performance',
  'javascript tips',
  'python django',
  'machine learning',
  'web development',
  'game design',
  'music production',
  'video editing',
  'photography tips'
];

export default function () {
  const query = searchQueries[Math.floor(Math.random() * searchQueries.length)];
  
  const res = http.get(`${BASE_URL}/api/search?q=${encodeURIComponent(query)}&page=1&limit=20`);
  
  check(res, {
    'search status is 200': (r) => r.status === 200,
    'search response time < 200ms': (r) => r.timings.duration < 200,
    'results returned': (r) => {
      const body = JSON.parse(r.body);
      return body.videos && body.videos.length > 0;
    },
  });
  
  sleep(Math.random() * 3 + 1); // Random sleep between 1-4 seconds
}
