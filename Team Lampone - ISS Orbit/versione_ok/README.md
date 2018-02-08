
## Team name

Team Lampone

## Number of team members

4

## Student age group

11 to 13 years


## What are the main objectives of your mission?

We want to investigate the ISS orbit, by estimating the variation of the station speed using the images captured from the external view. The station currently provides openly information such as its actual speed, which we can use as reference to validate our findings. Also, we would like to explore how often engines are switched on in order to keep the ISS at the correct altitude and speed. The continuous reading of acceleration and speed could provide relevant signals to analyze.

## Describe how you will achieve your mission objectives

We use the accelerometer, gyroscope, camera (external view), the led display, and also need a correct time. These components allow us to capture graphic and motion information, and provide a visual feedback. We obtain the velocity estimate by analyzing the offset of two consecutive partially overlapping images. By using OpenCV stitching classes and SIFT functions, it is possible to obtain an estimate of the pixels required to match two shapes found in the pictures which correspond to the same object (like mountains, clouds, etc). From camera hardware parameters and ISS height calculated with PyEphem, we can derive how many kilometers the ISS traveled between taking the two pictures.
Images are taken every 12 secs (regardless of sun exposition) and saved on filesystem with the timestamp in the filename, so this sequence will allow us to reconstruct the velocity. Sensors data from gyroscope and accelerometer will be used to correct the offset in pixel of images, by removing the component given by pitch, roll, and yaw of the ISS. Such data is taken every sec and written to disk every 20. The estimate will be calculated offline in the 4th phase, with code from this Github repo (to be refined): http://bit.ly/2sd69jL

## What do you think the results from the ISS will be? Explain your prediction

We expect to detect a constant velocity of ISS, around 28.000 Km/h within some error margin due to image resolution and imprecise calculation of the station height. We already tested OpenCV stitching functionality on old images from the previous editions: with a picture taking interval of 12 seconds we obtain enough overlap to get good stitching, so we expect the derived velocity to be reasonably accurate. With some luck, we could also detect the vertical velocity in the case of rockets are used to reposition the station. To assess the quality of the analysis, obtained data will be then matched with real-time data from ISS sensors (https://isslive.com). The system developed for velocity calculation will be also reused in our CoderDojo group to determine velocity of terrestrial vehicles and robots.

## Does your experiment require the blue filter?

No

## Please estimate how much disk space your experiment will use, on the Astro Pi computer, in MegaBytes

3,000


