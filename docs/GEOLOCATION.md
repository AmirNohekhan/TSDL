# Geolocation Conventions

Image coordinates originate at the top-left. The reference Python camera frame follows OpenCV:
`+x` image-right, `+y` image-down, `+z` optical-forward. Pixel rays are calculated only after
undoing model letterboxing/cropping and rotation into the calibrated source-image coordinates.

For a bounding box, the default first-pass reference is its center. This is the visual sign-face
center, not necessarily the physical post coordinate. The convention is stored on each
observation so later models can use bottom-center, segmentation keypoints, or a learned anchor.
Lens distortion must be removed before the pinhole projection whenever calibrated coefficients
are available.

World calculations should use a local East-North-Up metric frame anchored near the session.
WGS84 values are ordered latitude, longitude, altitude and converted through ECEF. Transform
composition must explicitly represent camera-to-device, mount/device-to-vehicle, and
vehicle-to-ENU rotations; Android display rotation is not a world orientation.

Triangulation estimates a point from multiple timestamp-aligned camera origins and unit world
rays. Confidence is not uncertainty. Observation weights may include pixel covariance, GNSS
accuracy, orientation uncertainty, calibration grade, detection confidence, blur, sign size,
and view angle, but each mapping must be calibrated rather than invented.

An estimate is not inventory-ready until policy checks positive ray depth, observation count,
vehicle baseline, angular diversity, residual, GNSS quality, and propagated horizontal
uncertainty. Monocular size estimates must use a separate method label and wider uncertainty.

