// testFriendsBackend.js
// Run with: node testFriendsBackend.js

import fetch from "node-fetch";

// Replace with a valid access token for your user
const ACCESS_TOKEN = "eyJhbGciOiJIUzI1NiIsImtpZCI6InJsbXd6SmM1aFJXUmVlRmQiLCJ0eXAiOiJKV1QifQ.eyJpc3MiOiJodHRwczovL2didnl2ZWFpZnZxbmV5YXlsb2tzLnN1cGFiYXNlLmNvL2F1dGgvdjEiLCJzdWIiOiI1NGE2MjU2MS02ODJjLTQyOWItOWRmNS0xODE0NWUzOTMwYzciLCJhdWQiOiJhdXRoZW50aWNhdGVkIiwiZXhwIjoxNzY0MDExOTgzLCJpYXQiOjE3NjQwMDgzODMsImVtYWlsIjoiZGNoYXYyMEBnbWFpbC5jb20iLCJwaG9uZSI6IiIsImFwcF9tZXRhZGF0YSI6eyJwcm92aWRlciI6ImVtYWlsIiwicHJvdmlkZXJzIjpbImVtYWlsIl19LCJ1c2VyX21ldGFkYXRhIjp7ImVtYWlsIjoiZGNoYXYyMEBnbWFpbC5jb20iLCJlbWFpbF92ZXJpZmllZCI6dHJ1ZSwicGhvbmVfdmVyaWZpZWQiOmZhbHNlLCJzdWIiOiI1NGE2MjU2MS02ODJjLTQyOWItOWRmNS0xODE0NWUzOTMwYzcifSwicm9sZSI6ImF1dGhlbnRpY2F0ZWQiLCJhYWwiOiJhYWwxIiwiYW1yIjpbeyJtZXRob2QiOiJwYXNzd29yZCIsInRpbWVzdGFtcCI6MTc2MzkzOTk2NX1dLCJzZXNzaW9uX2lkIjoiMDg5NWI1ZmYtMjM3Mi00YjY4LTk4MWQtMmQxYjUyNDIyZjRlIiwiaXNfYW5vbnltb3VzIjpmYWxzZX0.fAFt-cAZNAMzyI9cHPwLCgtHOZ1PtO5tk_WwJq9nYic";

const BASE_URL = "http://127.0.0.1:5000";


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

// ----------------------------
// Run tests
// ----------------------------
async function runTests() {
//   console.log("Adding friend...");
//   await testAddFriend();

//   console.log("\nListing friends...");
//   await testListFriends();
}

runTests();