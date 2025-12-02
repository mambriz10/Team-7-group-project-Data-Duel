// Run: node test.js
// Make sure to: npm install node-fetch@2

const fetch = require("node-fetch");

// Use config.js for API URL
import { API_URL as BASE_API_URL } from './config.js';
const API_URL = `${BASE_API_URL}/person/update-activities`;

async function testUpdateActivities() {
    // Mock weekly activities payload
    const payload = {
        activities: {
            monday: [
                {
                    id: 1,
                    distance: 5000,
                    moving_time: 1500,
                    average_speed: 3.3,
                    max_speed: 6.0,
                    start_date: "2025-11-17T10:00:00Z",
                    type: "Run"
                }
            ],
            tuesday: [
                {
                    id: 2,
                    distance: 8000,
                    moving_time: 2400,
                    average_speed: 3.5,
                    max_speed: 7.2,
                    start_date: "2025-11-18T10:00:00Z",
                    type: "Run"
                }
            ],
            wednesday: [], // Empty day is fine
            thursday: [
                {
                    id: 3,
                    distance: 3000,
                    moving_time: 1000,
                    average_speed: 3.0,
                    max_speed: 5.5,
                    start_date: "2025-11-20T10:00:00Z",
                    type: "Run"
                }
            ]
        }
    };

    try {
        console.log("Sending test request to backend...");

        const response = await fetch(API_URL, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payload)
        });

        const data = await response.json();
        console.log("Status:", response.status);
        console.log("Response:", data);
    } catch (err) {
        console.error("Error testing backend:", err);
    }
}

testUpdateActivities();
