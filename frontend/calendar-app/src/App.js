import React, { useState } from "react";
import FullCalendar from "@fullcalendar/react";
import dayGridPlugin from "@fullcalendar/daygrid";
import timeGridPlugin from "@fullcalendar/timegrid";
import interactionPlugin from "@fullcalendar/interaction";
import "./App.css";

// Calendar App 
// Allows users to upload schedule.json and overrides.json data,
// sends it to the backend to generate an optimized schedule,
// then displays the resulting schedule in both calendar and list views.

// example schedule.json:
/*
{
  "users": [
    "alice",
    "bob",
    "charlie"
  ],
  "handover_start_at": "2025-11-07T17:00:00Z",
  "handover_interval_days": 7
}
*/

// example overrides.json:
/*
[
  {
    "user": "charlie",
    "start_at": "2025-11-10T17:00:00Z",
    "end_at": "2025-11-10T22:00:00Z"
  }
]
*/ 

// example answer format from backend:
/*
[
  {
    "user": "alice",
    "start_at": "2025-11-07T17:00:00Z",
    "end_at": "2025-11-14T17:00:00Z"
  },
  {
    "user": "bob",
    "start_at": "2025-11-14T17:00:00Z",
    "end_at": "2025-11-21T17:00:00Z"
  }
]
*/




function App() {

  // State variables
  const [scheduleJson, setScheduleJson] = useState("");
  const [overridesJson, setOverridesJson] = useState("");
  const [response, setResponse] = useState(null);
  const [from, setFrom] = useState("2025-11-07T17:00:00Z");
  const [until, setUntil] = useState("2025-11-21T17:00:00Z");

  const cssColors = [
    "var(--sunset)",
    "var(--vanilla)",
    "var(--tea-green)",
    "var(--celadon)",
    "var(--emerald)",
    "var(--cambridge-blue)",
    "var(--cadet-gray)",
    "var(--slate-gray)",
    "var(--chinese-violet)",
  ];

  const handleSubmit = async () => {
    try {
      const scheduleData = JSON.parse(scheduleJson);
      const overridesData = JSON.parse(overridesJson);

      const res = await fetch("/schedule", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          schedule: scheduleData,
          overrides: overridesData,
          from,
          until,
        }),
      });

      const data = await res.json();

      // Extract unique users from the response
      const uniqueUsers = [...new Set(data.map((e) => e.user))];

      // Assign a random color to each user
      const userColors = {};
      uniqueUsers.forEach((user) => {
        const randomIndex = Math.floor(Math.random() * cssColors.length);
        userColors[user] = cssColors[randomIndex];
      });

      // Map events for FullCalendar
      const mappedEvents = data.map((e) => ({
        title: e.user,
        start: e.start_at,
        end: e.end_at,
        color: userColors[e.user],
        allDay: false,
      }));

      setResponse(mappedEvents);
    } catch (err) {
      alert("Invalid JSON or network error: " + err.message);
    }
  };

  const events = response || [];

  return (
    <div className="App">
      <h2>User Schedule Calendar</h2>
      <div className="calendar-container">
        {/* 📋 List View */}
        <div className="event-list">
          <h3>Event List</h3>
          <div>
            {events.map((event, i) => {
              const startDate = new Date(event.start);
              const endDate = new Date(event.end);

              const options = {
                month: "short",
                day: "numeric", // e.g., "7"
                hour: "numeric",
                minute: "2-digit",
                hour12: true, // AM/PM
              };

              const formattedStart = startDate.toLocaleString([], options); // e.g., "Nov 7, 5:00 PM"
              const formattedEnd = endDate.toLocaleString([], options);

              return (
                <div
                  key={i}
                  className="event-item"
                  style={{
                    borderLeft: `4px solid ${event.color}`,
                    color: event.color,
                  }}
                >
                  <strong>{event.title}</strong>
                  <br />
                  <span>
                    {formattedStart} → {formattedEnd}
                  </span>
                </div>
              );
            })}
          </div>
        </div>

        {/* 🗓️ Calendar View */}
        <div className="calendar">
          <FullCalendar
            plugins={[dayGridPlugin, timeGridPlugin, interactionPlugin]}
            initialView="timeGridWeek"
            slotMinTime="06:00:00"
            slotMaxTime="24:00:00"
            events={events}
            height="90vh"
          />
        </div>
      </div>

      {/* 📝 Second container for JSON input */}
      <div
        className="json-input-container"
        style={{
          minHeight: "70vh",
          width: "auto",
          padding: "1rem",
          background: "#f4f4f4",
        }}
      >
        <h3>Upload Schedule and Overrides</h3>
        <div style={{ display: "flex", gap: "1rem", flexWrap: "wrap" }}>
          <textarea
            style={{ flex: 1, minHeight: "60vh" }}
            placeholder="Paste schedule.json here"
            value={scheduleJson}
            onChange={(e) => setScheduleJson(e.target.value)}
          />
          <textarea
            style={{ flex: 1, minHeight: "60vh" }}
            placeholder="Paste overrides.json here"
            value={overridesJson}
            onChange={(e) => setOverridesJson(e.target.value)}
          />
        </div>

        {/* Inputs for from/until and submit button */}
        <div
          style={{
            display: "flex",
            alignItems: "center",
            gap: "1rem",
            marginTop: "1rem",
          }}
        >
          <label>
            From:
            <input
              type="datetime-local"
              value={from.slice(0, 16)} // slice for input compatibility
              onChange={(e) => setFrom(new Date(e.target.value).toISOString())}
              style={{ marginLeft: "0.5rem" }}
            />
          </label>
          <label>
            Until:
            <input
              type="datetime-local"
              value={until.slice(0, 16)}
              onChange={(e) => setUntil(new Date(e.target.value).toISOString())}
              style={{ marginLeft: "0.5rem" }}
            />
          </label>
          <button
            onClick={handleSubmit}
            style={{ padding: "0.5rem 1rem", fontSize: "1rem" }}
          >
            Submit
          </button>
        </div>
      </div>
    </div>
  );
}

export default App;
