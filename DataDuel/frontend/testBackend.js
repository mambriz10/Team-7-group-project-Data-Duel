// testFriendsBackend.js
// Run with: node testFriendsBackend.js

import fetch from "node-fetch";

// Replace with a valid access token for your user
const ACCESS_TOKEN = "eyJhbGciOiJIUzI1NiIsImtpZCI6InJsbXd6SmM1aFJXUmVlRmQiLCJ0eXAiOiJKV1QifQ.eyJpc3MiOiJodHRwczovL2didnl2ZWFpZnZxbmV5YXlsb2tzLnN1cGFiYXNlLmNvL2F1dGgvdjEiLCJzdWIiOiI1NGE2MjU2MS02ODJjLTQyOWItOWRmNS0xODE0NWUzOTMwYzciLCJhdWQiOiJhdXRoZW50aWNhdGVkIiwiZXhwIjoxNzY0MDI4MDg2LCJpYXQiOjE3NjQwMjQ0ODYsImVtYWlsIjoiZGNoYXYyMEBnbWFpbC5jb20iLCJwaG9uZSI6IiIsImFwcF9tZXRhZGF0YSI6eyJwcm92aWRlciI6ImVtYWlsIiwicHJvdmlkZXJzIjpbImVtYWlsIl19LCJ1c2VyX21ldGFkYXRhIjp7ImVtYWlsIjoiZGNoYXYyMEBnbWFpbC5jb20iLCJlbWFpbF92ZXJpZmllZCI6dHJ1ZSwicGhvbmVfdmVyaWZpZWQiOmZhbHNlLCJzdWIiOiI1NGE2MjU2MS02ODJjLTQyOWItOWRmNS0xODE0NWUzOTMwYzcifSwicm9sZSI6ImF1dGhlbnRpY2F0ZWQiLCJhYWwiOiJhYWwxIiwiYW1yIjpbeyJtZXRob2QiOiJwYXNzd29yZCIsInRpbWVzdGFtcCI6MTc2MzkzOTk2NX1dLCJzZXNzaW9uX2lkIjoiMDg5NWI1ZmYtMjM3Mi00YjY4LTk4MWQtMmQxYjUyNDIyZjRlIiwiaXNfYW5vbnltb3VzIjpmYWxzZX0.5_IjZMsRmyeyvrUufudAtNmejZVfZiBFOgo1aTnK5JM";

// Use config.js for API URL
import { API_URL } from './config.js';
const BASE_URL = API_URL;


const F2 = "ed0edb23-40c3-43fb-abdf-e3dd41b0072d";
const leaderboardID1 = "ed0edb23-40c3-43fb-abdf-e3dd41b0072d";
// Helper to call backend with token
async function callBackend(endpoint, body) {
  const res = await fetch(`${BASE_URL}${endpoint}`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(body),
  });
  const data = await res.json().catch(() => ({}));
  return { status: res.status, data };
}

// ----------------------------
// Test adding a friend
// ----------------------------
async function testAddFriend() {
    const testFriendId = "7ef20984-6b83-4e6e-b3fe-1c315b9ee6cb"
    const { status, data } = await callBackend("/friends/add", {
        access_token: ACCESS_TOKEN,
        friend_id: testFriendId,
    });
    console.log("=== /friends/add ===");
    console.log("Status:", status);
    console.log("Data:", data);
}

// ----------------------------
// Test listing friends
// ----------------------------
async function testListFriends() {
    const { status, data } = await callBackend("/friends/list", {
        access_token: ACCESS_TOKEN,
    });

    // Flatten and remove nulls
    const friendsNested = data.friends || [];
    const friends = friendsNested.flat().filter(f => f !== null);

    friends.forEach(friend => {
        console.log("Friend username:", friend.username);
        console.log("Friend user_id:", friend.user_id);
    });

}

async function testCreateLeaderboard() {
    console.log("=== Test: Create Leaderboard ===");
    const testFriendId = "7ef20984-6b83-4e6e-b3fe-1c315b9ee6cb" 
    const body = {
        access_token: ACCESS_TOKEN,
        name: "My Test Leaderboard",
        metric: "total_distance",
        members: [
        testFriendId
        ]
  };

  const { status, data } = await callBackend("/leaderboard/create", body);

  console.log("Status:", status);
  console.log("Response:", data);
}

async function testAddMember() {
  const testLeaderboardId = "69facc6b-92f8-404f-b364-15da4b309175";
  const testUserId = F2;

  const { status, data } = await callBackend("/leaderboard/add_member", {
    access_token: ACCESS_TOKEN,
    leaderboard_id: testLeaderboardId,
    user_id: testUserId
  });

  console.log("=== /leaderboard/add_member ===");
  console.log("Status:", status);
  console.log("Data:", data);
}

// Test fetching user-specific leaderboards
async function testGetUserLeaderboards() {
  const { status, data } = await callBackend("/leaderboards/my", {
    access_token: ACCESS_TOKEN,
  });

//   "Data: {
//   "joined": [],
//   "owned": [
//     {
//       "created_at": "2025-11-24T22:48:39.349184",
//       "creator_id": "54a62561-682c-429b-9df5-18145e3930c7",
//       "id": "69facc6b-92f8-404f-b364-15da4b309175",
//       "members_count": 2,
//       "metric": "total_distance",
//       "name": "My Test Leaderboard"
//     }
//   ]
//     }"

  console.log("=== POST /leaderboards/my ===");
  console.log("Status:", status);
  console.log("Data:", JSON.stringify(data, null, 2));
}
// ----------------------------
// Run tests
// ----------------------------
async function runTests() {
//   console.log("Adding friend...");
//   await testAddFriend();

//   console.log("\nListing friends...");
//   await testListFriends();

//  testing the create leaderboard
//  testCreateLeaderboard();

//  testing the add to leaderboards;
    // console.log("adding member test\n");
    // testAddMember();

    console.log("viewing my lederboards\n");
    testGetUserLeaderboards();
}

runTests();