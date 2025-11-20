// API Controllers Directory
// This directory contains HTTP route handlers with intentional performance issues

/*
PERFORMANCE ISSUES IN THIS DIRECTORY:
1. N+1 Query Problems - Multiple database queries in loops
2. No pagination - Loading all records at once
3. No caching - Every request hits the database
4. Sequential operations - Independent queries executed one by one
5. No error handling - Poor exception management
6. Memory leaks - Inefficient data structures

Each controller file demonstrates real-world performance anti-patterns
that workshop participants will optimize using GitHub Copilot agents.
*/

module.exports = {
  videoController: require('./videoController'),
  feedController: require('./feedController'),
  searchController: require('./searchController'),
  recommendController: require('./recommendController'),
  commentController: require('./commentController')
};
