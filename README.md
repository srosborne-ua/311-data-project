Chicago 311 Service Equity Analysis

Do lower-income neighborhoods wait longer for city services in Chicago?

This project analyzes over a year of Chicago 311 service request data across all 77 community areas to test whether neighborhood income level predicts how quickly the city responds to non-emergency service requests such as potholes, graffiti, abandoned vehicles, sanitation issues, etc.

Data Source: Chicago 311 Data Portal

tech stack: The data starts as raw CSVs pulled from the Chicago Data Portal and is extracted and loaded with Python. A lot of cleaning work is then handled with polars. The data was then loaded into a postgreSQL database for analysis including aggregating response times by community area and request type, computing the correlation between income and response time, and running the window functions behind the seasonal breakdown. The results are exported as pre-aggregated CSVs and brought into Tableau, which is used purely for visualization

VIEW THE INTERACTIVE TABLEAU DASHBOARD HERE: https://public.tableau.com/app/profile/sage.osborne/viz/Chicago_311_Data_Project/map_dashboard


The Finding:
My initial hypothesis going in was that lower-income neighborhoods would see slower response times. the data actually contradicts this 
presupposition

Across Chicago's 77 community areas, the percentage of low-income residents is negatively correlated with average 311 response time (r = -0.51). In summary, neighborhoods with a higher proportion of low-income residents tend to get slightly faster average response times on average, not slower ones.

Dashboard explanation:
Two maps of Chicago's community areas sit next to each other. One shaded by average 311 response time, the other shaded by percentage of low-income residents. There's a slight inverse pattern across the city, but it's a loose trend. plenty of community areas defy thius rule in both directions, and the relationship only really shows itself when you look at the city as a whole rather than area by area.

It's possible the headline correlation isn't really about income at all, but about what kind of requests get filed in different neighborhoods. Low-income and high-income areas might just report different mixes of complaints (more pothole reports here, more tree-trimming requests there), and some complaint types naturally get closed faster than others. To check for that, average response time is broken out by SR (service request) type separately for low-income and high-income community areas. allthough it appears high income areas may be slightly more likely to make less urgent requests,
Their is not enogh of a difference in request type across income brackets to argue that it could cause any disparity to be obscured. diffences in request types across income brackets can be ruled out as something that might cover up an underlying disparity.

Bonus, less related to main thesis:
One intersting thing: the strongest corralation for service response time I found was not based on income, it was based on the month that the service request was made in. This suggests the biggest factor affecting service times was the overall demand being made on the 311 system, as it was the bussiest months that had the longest service times
