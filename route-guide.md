# Running Route Generation System – Implementation Guide

This guide outlines a comprehensive approach to building a running route generation system using the Strava API, Google Maps API (or a suitable alternative), and an LLM-powered user input flow. The system will interpret natural language route requests, generate candidate routes matching the user's preferences, and return the top options with summaries and map visualizations. We also cover UI considerations, API usage, architecture, example workflows, and recommendations for an MVP versus stretch goals.

---

## Overview and Architecture

The system combines multiple components: an LLM for natural language understanding, external APIs for route data (Strava, Google Maps), a backend server for orchestration, and a frontend UI for user interaction and visualization. The high-level architecture is as follows:

### Core Components

1. **User Interface (UI)**: Accepts user input (free-text prompt and optional structured controls like sliders/checklists) and displays the resulting routes on a map.

2. **LLM Parsing Module**: Receives the user's natural language description and translates it into structured route constraints (distance, location, preferences, etc.).

3. **Route Generation Engine**: Uses the structured constraints to query route data and generate candidate routes. This involves calling the Strava API for popular segments/routes and the Google Maps (Directions/Routes) API (or alternative routing service) to construct actual paths that meet the criteria.

4. **Scoring & Selection**: Ranks the candidate routes based on how well they match user preferences (e.g. scenic value, distance match, minimal road crossings).

5. **Persistence Layer**: Stores generated routes and their metadata in a database for future reuse or user review.

6. **Backend Server**: Coordinates the above components – handling API calls, running the LLM prompt, querying databases – and exposes endpoints for the frontend.

### External APIs

- **Strava API** – provides data on popular running segments and existing routes. Requires OAuth authentication for access ([developers.strava.com](https://developers.strava.com)).
- **Google Maps API** – provides routing (directions) between waypoints and static/interactive map visuals. Alternatively, Mapbox or OpenStreetMap-based services can be used for routing and maps.

### System Data Flow

A typical flow begins with the user describing their desired run. The UI sends this input to the backend, which invokes the LLM to parse the request. The backend then uses the parsed constraints to fetch route data (Strava segments or saved routes) and calls the Maps API to generate detailed route paths (polylines, distances, etc.). Multiple candidate routes are assembled, scored, and returned to the frontend, which displays the top 3 (or more) options with summary info and an interactive map for each route. The route information is also saved in the database for later retrieval or analysis.

> **Architecture Diagram Note**: An architecture diagram illustrating the components and flow would show the user/front-end on one side, the LLM and backend logic in the middle, and the Strava/Maps APIs plus database on the other side, with arrows indicating data flow such as: user prompt → LLM → constraints → Strava/Maps → route results → front-end.

---

## Natural Language Input & LLM Constraint Parsing

### User Prompt

The user can input a request like:

> *"I want a 5-mile scenic run near the lake with minimal road crossings."*

The system should also provide optional UI controls for clarity – for example:
- A slider to adjust target distance
- Checkboxes for preferences like "avoid highways" or "trail only"
- Dropdowns for surface type

These controls serve as a structured override or supplement to the LLM's understanding.

### LLM Role

The LLM (e.g. GPT-4 via OpenAI API) interprets the natural language and produces a structured representation of the route constraints. One approach is to prompt the LLM to extract parameters and output a JSON object or a Python dictionary. For example:

- **Distance**: Target ~5 miles (could be a range, e.g. 4.5–5.5 miles)
- **Location**: "near the lake" – likely referring to a specific lake or area. The LLM might infer a location name (e.g. "Lake Michigan, Chicago" if the user's context or profile suggests Chicago)
- **Scenic Preference**: True (user said "scenic run" – implies route should include aesthetic areas like parks, waterfronts)
- **Road Crossings**: Minimal – implies preference for uninterrupted paths (trails/parks) and possibly using `avoid_highways` or avoiding busy intersections
- **Route Type**: Could infer a loop if not stated, since runners often prefer loop routes for convenience (or could leave unspecified). The phrase "run near the lake" might imply a loop around part of the lakefront
- **Surface type**: Possibly trails or pedestrian paths (if user said scenic, likely off main roads)

### Example LLM Output

The LLM might return something like:

```json
{
  "distance": {"min": 4.8, "max": 5.2, "unit": "miles"},
  "location": "Lake Michigan shoreline in Chicago, near downtown",
  "preferences": {
    "scenic": true,
    "avoid_highways": true,
    "avoid_traffic": true,
    "include_waterfront": true
  },
  "route_type": "loop",
  "notes": "Focus on lakefront trail or park paths; minimize street crossings."
}
```

This structured data will then be used by the backend logic. In implementation, you could use OpenAI's function calling feature or a fine-tuned model to ensure consistent JSON output. Basic prompt-engineering might suffice: for instance, instructing *"Extract the following fields: distance, location, preferences…"* and giving examples.

### Disambiguation

If the user input is vague or missing key details (e.g., which lake? current location?), the LLM or backend can handle it by either:

- **(a)** Asking a clarifying question via the UI (if interactive), or
- **(b)** Using defaults

For an MVP, you might assume a default location (such as the user's known city from profile or IP) when not specified. The LLM could potentially guess the likely intended location from context (for example, if the user profile indicates they are in Illinois and they say "near the lake," it might infer Lake Michigan).

---

## Generating Candidate Routes with Strava and Maps APIs

Once we have structured constraints, the system generates route candidates. This involves two sub-tasks: finding potential route segments/waypoints (content) and constructing a route path (geometry).

### Using Strava API for Route Content

#### Why Strava?

Strava's data can help identify popular running routes and trail segments that match the user's preferences. Strava segments are user-defined stretches of road or trail that often correspond to popular routes (e.g., a well-known park loop or waterfront trail). Strava also allows users to save and share routes. Leveraging this data can ensure our recommendations feel "scenic" and runner-approved, rather than arbitrary.

#### Authentication

To use the Strava API, you must register an app with Strava and obtain OAuth credentials. Every request needs an access token from an authenticated Strava account (for a public data scope) ([developers.strava.com](https://developers.strava.com)). For development, you might authenticate once with your own account and use that token (assuming only public segment data is needed). If you later allow users to connect their own Strava account (stretch goal), you'd implement the OAuth flow to get user-specific tokens.

#### Strava Segment Explorer

Strava provides an endpoint to explore segments within a geographic area. By calling `/segments/explore` with a bounding box and activity type, you can get the top 10 segments in that region ([developers.strava.com](https://developers.strava.com)). We can use this to find scenic or popular segments near the desired location:

- **Bounding Box**: Determine a search area based on the user's location input. For example, if location is "Lake Michigan in Chicago," we geocode that to a lat/long and define a bounding box around it (a few mile radius).
- **Activity Type**: Use `running` to get running segments ([developers.strava.com](https://developers.strava.com)).
- **Result**: The API returns an `ExplorerResponse` with up to 10 segments (each with an ID, name, distance, coordinate bounds, and climb category). These are typically sorted by popularity (Strava's internal score).

Using Segment Explorer, we can gather candidate pieces of routes. For instance, around Chicago's lakefront, the explorer might return the "Lakeshore Path" segment (a popular waterfront trail ~3.9 miles) and others in parks. In fact, Strava's data analysis has identified the Lakefront Trail as one of the most heavily used routes in Chicago ([runnersworld.com](https://www.runnersworld.com)), underscoring that it's a prime scenic route.

#### Segments to Route Conversion

A segment is just a portion of a route, not necessarily a full loop. To build a runnable route from segments:

- We could use one long segment as the core of our route (e.g., Lakeshore Path segment). If it's shorter than desired distance, consider an out-and-back extension or connecting multiple segments.
- If multiple segments can connect, combine them. E.g., a scenic route might link two park trail segments via a short road section.
- For each candidate segment or combination, retrieve detailed info: Using the segment ID, call `/segments/{id}` to get details (including a polyline or a sequence of lat/long "stream" points if available via `/segments/{id}/streams`). The polyline gives the exact path of that segment ([developers.strava.com](https://developers.strava.com)).

Alternatively, if Strava Routes are available (for an authenticated user or through some public routes dataset), those could be used. Strava's API allows retrieving saved routes by ID (`/routes/{id}`) ([developers.strava.com](https://developers.strava.com)), which returns a series of waypoints and the full route polyline. For MVP, assume we rely on segments and our own route construction, since public routes might not be directly queryable without specific IDs.

#### Example

The system searches within the Chicago lakefront area and finds a segment for the "Chicago Lakeshore Path". This segment is ~3.9 miles and runs along Lake Michigan's edge (scenic, minimal intersections). It might also find a segment for "Lincoln Park Loop" (~2 miles) or "Lakefront North Extension". These become building blocks for route options.

---

### Using Google Maps API for Route Construction

#### Why Maps API?

Once we have key waypoints or path hints (from Strava or user input), we need to construct a full route polyline and get turn-by-turn details (distance, estimated time, etc.). Google Maps Directions API is a straightforward solution for routing:

- It can compute routes in **walking** or **cycling** mode (more appropriate for running than driving)
- It allows waypoints to shape the route path ([developers.google.com](https://developers.google.com))
- It supports parameters to avoid certain road types (e.g. highways) which can help in honoring "avoid major roads" preferences ([developers.google.com](https://developers.google.com))

#### Geocoding & Waypoints

First, geocode the user's location input if needed (Google Geocoding API or Places API can convert "near the lake in Chicago" to a coordinate or specific area). Decide on a start and end point:

- If the user doesn't specify a starting point, assume a convenient location near the area (for example, a trailhead or parking lot by the lake). For MVP in a single city, this could be hard-coded or chosen from a known set. For a general solution, we might choose the centroid of the requested area or the location of a popular segment as the start.
- If a **loop** is desired (start and end at same place), we will ultimately need to return to the start point. One method is to generate a route out to a distant waypoint and back to start in one request by specifying the start and end as the same and including intermediate waypoints.

#### Constructing a Route

Using Google Directions API:

- Set travel mode to **walking** (most closely matches running, and will use pedestrian paths where available) ([developers.google.com](https://developers.google.com))
- Include `avoid=highways` to steer clear of highways/major roads ([developers.google.com](https://developers.google.com)). (Walking directions typically won't go on highways anyway, but this is more relevant if using cycling or driving modes for some reason.)
- If "minimal road crossings" is a priority, purely algorithmic control is limited, but choosing pedestrian paths and parks via waypoints helps. We can insert waypoints at scenic locations – for example, a waypoint along the lakefront trail ensures the route goes through that trail. The Directions API supports multiple waypoints for walking routes ([developers.google.com](https://developers.google.com)). We can mark them as pass-through (`via:` waypoints) so the API doesn't treat them as separate stops but simply forces the route through them ([developers.google.com](https://developers.google.com)).

#### For Loop Routes

We may need to use trickery, as the Directions API normally finds the shortest path from A to A (which is trivial zero-length). One approach is:

- Pick an intermediate target point that is roughly half the desired distance away (e.g., 2.5 miles away along the lake). Get walking directions from Start → that point → back to Start by listing waypoints `[target, Start]` with `optimize:false`. Another approach is to divide into two routes (Start → target and target → Start separately) and combine them.
- Alternatively, provide a sequence of waypoints that form a loop. For example: Start at Point A, then waypoint B (somewhere 2.5 miles east), then waypoint C (somewhere 2.5 miles north of A), then end at A. The result should be a loop around A hitting B and C. This might require manual tuning of waypoints.
- If an **out-and-back** route is acceptable (less interesting, but simplest to ensure distance), one can take a single path (like a trail) and go out half the distance then return back. This is easy to generate: take the Strava segment polyline and split in half; or use Directions API from start to an endpoint and double the path (but ensure it follows same route back).

#### Route Data from API

The Google Directions API response will provide:

- The route **polyline** (encoded polyline string which can be decoded to a list of lat/long points)
- The total **distance** and **duration**
- **Step-by-step directions** (which we may not need to show fully, but could be used to count road crossings or identify surface types)
- If multiple routes are possible, it can provide **alternatives**; we might request alternate routes for diversity

We can also utilize Google Maps Routes Preferred API (a newer API) which has more advanced features, but for our scope, the standard Directions API suffices.

#### Alternate Routing Services

If not using Google, consider:

- **Mapbox Directions API** – similar capabilities, uses OpenStreetMap data. It also supports profile options (walking, cycling) and returns routes with distances.
- **OpenRouteService** or **GraphHopper** – open source routing engines that can run on OSM data, which might allow custom weighting (e.g., prioritize scenic paths or park trails).
- **Strava Route Builder API** – Strava itself has an internal routing engine using their heatmap data to generate popular routes given start/distance. However, this is not exposed via public API (it's used on their website and mobile app, but not documented for external use). Thus, we emulate it using the above methods.

---

### Assembling Candidate Routes

Using the data from Strava segments and the routing API, we generate several route candidates:

#### Route 1: Based on Most Popular Segment

e.g., incorporate the top Strava segment in the area. For the example prompt, Route 1 might follow the Lakefront Trail for ~5 miles. We could start at a known trail entry point and follow the shoreline. If the segment is 3.9 miles one-way, one option is an out-and-back totaling ~7.8 miles; but to meet ~5 miles, we might start in the middle of that segment and do a loop – for instance, a 2.5 mile out and back along the lake (which gives 5 miles total). Another option is to start at one end of the 3.9mi segment and end partway (making a 5mi one-way, but that wouldn't return to start). 

For MVP simplicity: we could present a ~4 mile route along the lake (the segment itself) and note it's a bit short, or extend it slightly with a small loop in a park to reach 5 miles.

#### Route 2: Combining Multiple Segments

e.g., connect the lakefront trail and a nearby park loop. In Chicago, one could run along the lake for 3 miles, then turn into Lincoln Park for 2 miles, and return to the start. Using two waypoints (one on the lake trail, one in the park), the Directions API can create a loop that covers both scenic areas.

#### Route 3: Avoiding All Busy Roads

Perhaps a route that is entirely inside a large park or along a waterfront path (even if it means doing multiple laps). For instance, a 5-mile route within Busse Woods (an 8-mile loop in a forest preserve) or multiple laps around a smaller lake. This route might be slightly less scenic than the waterfront but absolutely no road crossings. It depends on available options in the given area.

#### Route 4: Alternate Start/Finish or Shape

To provide options, we might generate one route that is a loop, another that is point-to-point (if the user can arrange pickup or doesn't mind not ending where they started), and another that is out-and-back on a single path. However, since most recreational runs start and end at the same spot (especially "near my home" or a parked car), focusing on loops or out-and-backs is safer.

### Scoring Routes

Each candidate route gets a score based on the constraints:

- Does it hit the scenic targets (e.g., % of route in parks or along water)?
- How close is the distance to desired (penalize if too short/long)?
- Number of road crossings or segments on busy roads (fewer is better)
- Elevation gain if that was a factor (not mentioned in prompt, but one could consider if user wants flat)

We can derive some of these from the route data: e.g., count intersections from the step instructions or whether the route step mentions "Crossing" etc., or use OSM data to check how many traffic lights might be on the path (a stretch feature).

The Strava segment popularity could also be a factor (assuming more popular = likely enjoyable route).

Finally, pick the **top 3 (or more)** scoring routes to return to the user.

---

## Frontend Implementation and UI Design

A polished UI will make it easy for users to input their preferences and understand the output routes. We recommend a web application (HTML5/JS) for broad accessibility (unless the team is more comfortable with native mobile, but web is suggested by project guidelines).

### Frontend Framework

Use a modern JavaScript framework like **React** (with create-react-app or Next.js) or Vue/Angular. React is a great choice for an interactive map interface and handling the form inputs for route preferences:

- You can create a form component for the natural language prompt and preference toggles (distance slider, checkboxes for "Avoid highways", "Loop route only", "Trail surface only", etc.)
- Use state management to keep track of user inputs and the returned routes

### Map Display

Integrate a mapping library to display routes:

- The **Google Maps JavaScript API** can embed an interactive map. After getting route polyline coordinates from the backend, you can use the Maps JS API to draw polylines on a map and mark start/finish points. Google's API also allows adding custom markers and info windows (for example, clicking a route could show details).
- Alternatively, **Leaflet.js** (an open-source map library) with OSM tiles can be used, or **Mapbox GL JS** if using Mapbox. For an MVP, Google Maps might be simplest if you're already using their Directions API; it ensures consistency in road/path data between generation and display.
- Each of the top 3 routes could be either displayed on one map (differentiated by color) or on separate small maps. A simple approach: show a list of routes, and when the user selects one, show it on a map widget.

### Route Summary UI

For each route option returned, present:

1. **Title/Name**: If the route goes through known trails or segments, you can name it (e.g., "Lakefront Trail Loop", "Lincoln Park Circuit"). The Strava segment names or local park names can help here.

2. **Distance & Est. Time**: Display the total distance (in user's preferred units, e.g., miles or km) and perhaps an estimated running time (you could assume a pace or just show distance for now).

3. **Description**: A short summary of the route highlighting features, e.g., *"Follows the Lake Michigan shoreline with panoramic water views, then loops back through Lincoln Park. Mostly flat and on dedicated paths, with two minor road crossings."* You can generate this text template using the data (scenic highlights, flat/hilly, etc.). For more natural descriptions, you might even leverage the LLM to generate a friendly blurb given the route context (stretch goal).

4. **Elevation profile (optional)**: If hilliness is a concern and data is available (Google's API can provide step elevations, or Strava segment data includes elevation gain), a small elevation chart could be shown. This is more of a stretch feature for visual polish.

### Example Output for the Prompt

**Route 1: Lakefront Scenic Loop** – 5.0 miles
> Starts at Navy Pier, follows the Lakefront Trail north with continuous lake views, then loops back via Lincoln Park trails. *Scenic highlights:* Lake Michigan shoreline, park greenery. *Road crossings:* 2 minor crosswalks. (Flat terrain)

**Route 2: Lakeshore Out-and-Back** – 4.0 miles (extendable to 5)
> A straightforward run along the Lakefront path. Begin at Ohio Street Beach and run north to North Avenue Beach, then return the same way. *Scenic:* Excellent – entire route is along the water. *Road crossings:* None (fully on lakeside trail). (Flat terrain; can extend past North Ave for extra mileage.)

**Route 3: Museum Campus to Park Loop** – 5.3 miles
> Start at Buckingham Fountain, run south around Museum Campus (views of skyline and Lake), then head north on the lakefront trail and do a loop around Grant Park. *Scenic:* High – lake views and iconic city park. *Road crossings:* Few (mostly paths, one underpass). (Mix of city sidewalks and park paths.)

*(These are illustrative examples; the actual routes would be backed by real coordinates and map imagery.)*

The UI would list these with a "View Map" option or embed a small map. The user can click to enlarge a map and even get turn-by-turn directions if desired (leveraging Google's directions response).

### Frontend–Backend Interaction

The frontend will send the user's query to a backend endpoint (e.g., a POST to `/generateRoute` with the prompt and selected preferences as JSON). The backend then orchestrates the LLM and API calls as described, and returns a JSON response containing route options. The frontend then renders those. Using a library like **Axios** or **Fetch API** in JS to handle the request/response is standard. Ensure to handle loading states (show a spinner while routes are being generated, since the LLM + multiple API calls may take a couple of seconds).

---

## Backend Implementation Details

### Technology

You can implement the backend in **Node.js** (Express or Next.js API routes) or **Python** (Flask/FastAPI). Choose whatever the team is comfortable with.

### Backend Responsibilities

1. **LLM API Call**: Use OpenAI's SDK (or another LLM provider) to send the prompt for parsing. Securely store the API keys (don't expose them to frontend).

2. **Strava API Calls**: Use the Strava Python or Node SDK, or simply direct HTTP requests with the `Authorization: Bearer <token>` header. (Strava's Swagger documentation provides example code in multiple languages ([developers.strava.com](https://developers.strava.com)).) You'll need to handle obtaining and refreshing the OAuth token. For an MVP, you might manually get a token from the Strava dev console (which can last several hours) and configure it in your app.

3. **Google Maps API Calls**: You can call the Directions API via an HTTP request to their REST endpoint. Constructing the URL with origin, destination, waypoints, mode, etc., or use Google's client libraries. Be mindful of API keys and restrict usage to your domains.

### Example API Call

Using the REST API (in pseudocode):

```
GET https://maps.googleapis.com/maps/api/directions/json?origin=41.867,-87.614
    &destination=41.867,-87.614
    &waypoints=via:41.900,-87.620|via:41.915,-87.630
    &mode=walking&avoid=highways&key=YOUR_API_KEY
```

This would request a walking loop route that goes through the two via points (in this case, coordinates along the lakefront and in the park). The response would be a JSON with routes. You'd parse out `routes[0].overview_polyline` (the encoded path) and `routes[0].legs` information (distance of each leg, etc.).

### Combining Data

The backend will likely perform steps:

1. Use LLM to get constraints
2. Geocode location (if needed) via Google Geocoding API
3. Call Strava `/segments/explore` with bounds around that location to get popular segments
4. Choose waypoints from those segments or decide on route shape
5. Call Google Directions API to get full route
6. Repeat for alternative variations
7. Score the routes, then return the top ones in the response

### Data Structures

Define a `RouteOption` object/structure to hold:
- polyline or coordinates
- distance
- estimated duration
- list of notable features (maybe names of parks or trails used)
- a text description

This is what you send back to the frontend.

### Persistent Storage

For MVP, a simple storage might be sufficient. For example, store generated routes in an in-memory list or a JSON file keyed by some hash of the request. However, for longer-term and multi-user support, use a **database**. A lightweight choice could be SQLite or PostgreSQL (if using Python, SQLAlchemy ORM can help; if Node, something like Prisma ORM or even just pg library).

The route table could have:
- an ID
- user (if applicable)
- timestamp
- starting area
- distance
- route polyline (maybe stored as a compressed polyline string or GeoJSON)
- perhaps a JSON blob of the preferences or summary

This way, if a user asks for "5-mile lake run" again, you could retrieve an existing route rather than recompute (or present it as previously generated). It also enables a feature where users can browse or tweak past routes.

### Logging & Monitoring

It's useful to log each request and the steps (LLM output, chosen segments, etc.) for debugging. Given that multiple external APIs are involved, ensure to handle errors gracefully (e.g., if Strava API fails or returns nothing in area, fallback to using Google alone to create a generic route; if Google Directions fails for a certain waypoint config, adjust waypoints or inform user).

### Code Snippet (Pseudocode)

Here's a simplified example in Python-like pseudocode tying some of these steps together:

```python
def generate_routes(prompt_text):
    # 1. Parse prompt via LLM
    llm_response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "system", "content": SYSTEM_INSTRUCTION}, 
                  {"role": "user", "content": prompt_text}]
    )
    constraints = parse_llm_response(llm_response)  # e.g., JSON loads
    
    location = constraints.get("location")
    distance_target = constraints.get("distance")  # e.g., {min: 4.5, max: 5.5}
    prefs = constraints.get("preferences")
    
    # 2. Geocode location to lat/long
    center = geocode(location)  # using Google Geocoding API
    
    # 3. Find popular segments via Strava
    bounds = calc_bounding_box(center, radius=5km)
    segments = strava.explore_segments(bounds=bounds, activity_type="running")
    # segments is a list of ExplorerSegment with fields like name, length, start_latlng, end_latlng
    
    # 4. Construct candidate routes
    candidates = []
    # Example candidate 1: Use top segment directly (out-and-back or loop if possible)
    if segments:
        top_seg = segments[0]
        seg_length = top_seg.distance  # in meters
        start_coord = top_seg.start_latlng or center
        end_coord = top_seg.end_latlng or None
        # If segment distance is close to desired, maybe use it one-way and then use same path back.
        if seg_length * 2 >= distance_target["min"]*1609 and end_coord:
            # plan out-and-back on this segment
            waypoints = f"{end_coord[0]},{end_coord[1]}|{start_coord[0]},{start_coord[1]}"
            route = google_directions(start=start_coord, end=start_coord, waypoints=waypoints, mode="walking", avoid_highways=prefs.get("avoid_highways"))
        else:
            # segment itself as route (one-way)
            route = google_directions(start=start_coord, end=end_coord or start_coord, mode="walking", avoid_highways=prefs.get("avoid_highways"))
        candidates.append(route)
    
    # Example candidate 2: Loop via two waypoints (e.g., scenic point and return through different path)
    scenic_point = None
    if segments:
        # choose a second segment or a point of interest (like midpoint of top segment)
        scenic_point = midpoint_of_polyline(segments[0].polyline) if hasattr(segments[0], 'polyline') else segments[0].end_latlng
    if scenic_point:
        # Use start = scenic_point, end = scenic_point with via through another point to form loop
        loop_wp = f"via:{scenic_point[0]},{scenic_point[1]}"
        route = google_directions(start=scenic_point, end=scenic_point, waypoints=loop_wp, mode="walking", avoid_highways=prefs.get("avoid_highways"))
        candidates.append(route)
    
    # 5. Score candidates
    for route in candidates:
        route.score = score_route(route, prefs, distance_target)
    candidates.sort(key=lambda r: r.score, reverse=True)
    
    # 6. Format top 3 routes for output (with summaries, etc.)
    return format_routes(candidates[:3])
```

> **Note**: The above pseudocode glosses over many details, like how `google_directions` and `strava.explore_segments` are implemented, error checking, etc. It's meant to illustrate the sequence of calls.

---

## MVP Priorities vs. Stretch Goals

Given a semester timeline, it's important to define a Minimum Viable Product and what features can be added as enhancements.

### MVP Features (Core Scope)

#### 1. Natural Language to Route

Basic prompt parsing using LLM. It should at least extract distance and a general location/area. Hard-code or constrain certain preferences initially (e.g., always avoid highways for running; assume scenic means use parks if available).

#### 2. Route Generation in a Limited Area

Start with a specific city or region (e.g., Chicago or a known locale). This limits complexity in finding routes. You can even pre-select a handful of scenic routes in that area and have the system match the closest one to the request (as a fallback if dynamic generation is hard).

#### 3. Single API Integration

If using both Strava and Google is too complex at first, choose one:
- You could initially skip Strava integration and use Google's Directions API alone to generate a route from the user's start location (perhaps doing something simple like a loop: go X/2 miles in one direction, then return). This ensures you can return a route of correct distance, though it might not be the most scenic. Then add Strava-based refinement once basic routing works.
- Alternatively, you could forgo the LLM initially and use just UI controls to get structured input (distance slider and a map to pick a location) to prove out the route generation. Then incorporate the LLM for the natural language convenience.

#### 4. Frontend with Map Display

Show one route result on a map (perhaps just the top result). Ensure the user can see the route and basic info.

#### 5. Persistent Storage (simple)

Save routes in memory or local storage so that if the user generates the same route again in one session it can be quickly retrieved. A full database might be set up later, but isn't needed on day one.

#### 6. Authentication & Keys

Securely manage API keys (likely stored server-side). For MVP, you might not implement user login at all; the Strava token can be your developer token.

---

### Stretch Goals (Extended Functionality)

#### 1. Broader Geographic Support

Once the core works in one area, expand to accept any location. This mainly means integrating a geocoding step and ensuring your Strava segment search covers the correct area. The good news is the logic largely remains the same for any city, aside from possibly needing to tune how you choose waypoints (some cities might not have obvious scenic segments, etc., so you might integrate a fallback like using Google Places to find "parks near X" as waypoints).

#### 2. Refined LLM Understanding

Handle more complex prompts. For example, *"I want a 10K trail run with at least 500 feet of elevation gain, no repeats"* or *"a 5-mile run that passes through downtown landmarks."* This would require extracting additional constraints (elevation, specific POIs) and possibly using the LLM to suggest waypoints ("landmarks" could be turned into actual locations via a second API call to Google Places).

#### 3. Interactive Refinement

After the LLM returns constraints, the system could confirm with the user: *"Do you want a loop route of ~5 miles near Lake Michigan?"* – giving the user a chance to adjust before generation. This could be done via UI or via a conversational agent style.

#### 4. Multiple Routes & Comparison

MVP returns 3 routes but could just list them. A stretch feature is allowing the user to compare them (side-by-side maps or an interactive toggle) or even combine aspects (e.g., let the user tell the system, *"Combine route 1 and 2"* or *"shorten route 3 to 4 miles"* and regenerate).

#### 5. Real-time Data Integration

Introduce traffic or weather overlays. For instance, if using an API like Google Traffic or if the time of day is known, you could avoid routes that are currently crowded (though for running, "traffic" might refer to foot traffic or safety at night – not straightforward without specialized data). Weather integration could simply warn if it's raining or show forecast for the route time, which is a nice touch but not critical to route planning itself.

#### 6. Elevation Profiles & Difficulty

Compute elevation gain from the route polyline (Google's Elevation API or Strava segment data). Then, if a user says "no hills", you could factor that into scoring (flat routes score higher for those users). Conversely, some may want hills for training.

#### 7. User Accounts and Route Saving

Allow users to sign up/login and save their favorite routes. This could integrate with Strava by letting them save the route to their Strava account. Since Strava API doesn't allow direct route creation via API, a workaround is to upload the route as a Strava activity (as a "planned workout") or instruct users how to import the GPX. Alternatively, just maintain saved routes in your own database for the user and perhaps provide a GPX download option. Strava's API does allow exporting a route to GPX if you have a route ID ([developers.strava.com](https://developers.strava.com)), so if you store the route and later create it manually in Strava, you can get that GPX.

#### 8. Improved Scenic Scoring

Use external datasets to identify "scenic" factors. e.g., whether the route goes through green space (you could cross-reference the polyline with a map of parks or water bodies). This could augment Strava popularity data.

#### 9. Performance & Scaling

If usage grows or routes become national/global, implement caching of popular areas, rate limit management (Strava's rate limit is typically 100 requests per 15 minutes and 1000 per day for free tier), and possibly map tile caching. For example, if many users ask for "5 mile run in Central Park", you don't want to hit Strava and Google every single time anew.

---

## Conclusion

This system blends cutting-edge AI (LLM for natural language understanding) with reliable geo-APIs to create a unique running route planner. By starting with a focused scope (MVP) and gradually layering in data sources and features, a student team can implement a functional prototype within a semester and have clear paths to enhance it. The end result will be an application where runners can simply describe their dream run and immediately receive a few tailored route options – complete with maps and details – ready to explore, whether in their local neighborhood or on their next travel adventure.

---

## References

### Strava API Documentation

- [Strava Developers - API Reference](https://developers.strava.com/docs/reference/)
- [Strava Segments - Explore Segments](https://developers.strava.com/docs/reference/#api-Segments-exploreSegments)

### Google Maps API Documentation

- [Getting Directions - Directions API](https://developers.google.com/maps/documentation/directions/get-directions)

### Related Articles

- [The Best Strava Routes in Every Major City for Runners - Runner's World](https://www.runnersworld.com/races-places/g20730330/the-most-popular-running-routes-in-the-20-biggest-us-metro-areas/)

---

## Citations

### All Sources

**Strava Developers**
- https://developers.strava.com/docs/reference/

**Google Developers**
- https://developers.google.com/maps/documentation/directions/get-directions

**Runner's World**
- https://www.runnersworld.com/races-places/g20730330/the-most-popular-running-routes-in-the-20-biggest-us-metro-areas/
