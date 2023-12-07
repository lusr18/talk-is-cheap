-- Create db
-- CREATE DATABASE workout_tracker;


-- Create user table
CREATE TABLE user (
    id             INT AUTO_INCREMENT PRIMARY KEY NOT NULL,
    username       VARCHAR(50) NOT NULL,
    password       VARCHAR(255) NOT NULL,
    email          VARCHAR(255) NOT NULL,
    age            INT NOT NULL,
    gender         INT NOT NULL
);



-- Create workout log table
CREATE TABLE workout (
    workout_id      INT AUTO_INCREMENT PRIMARY KEY NOT NULL,
    workout_date    DATE NOT NULL,
    exercise_name   VARCHAR(50) NOT NULL,
    sets            INT NOT NULL,
    reps            INT NOT NULL,
    weight          DECIMAL(5,2),
    duration        DECIMAL(5,2), -- Duration in minutes
    notes           VARCHAR(255)
);

-- Create personal tracker table, tracks weight, height, body fat percentage
CREATE TABLE personal_tracker (
    tracker_id              INT AUTO_INCREMENT PRIMARY KEY NOT NULL,
    record_date             DATE NOT NULL,
    weight                  DECIMAL(5,2) NOT NULL,
    height                  DECIMAL(5,2) NOT NULL,
    body_fat_percentage     VARCHAR(255)
);




-- Random data for testing
INSERT INTO workout (workout_id, workout_date, exercise_name, sets, reps, weight, notes) VALUES
(1, '2023-12-01', 'Bench Press', 4, 10, 56, ''),
(2, '2023-12-01', 'Squats', 4, 12, 80, ''),
(3, '2023-12-01', 'Deadlift', 3, 8, 100, ''),
(4, '2023-12-01', 'Pull-ups', 3, 10, NULL, 'Bodyweight'),
(5, '2023-12-01', 'Overhead Press', 3, 10, 40, ''),
(6, '2023-12-02', 'Barbell Row', 3, 10, 50, ''),
(7, '2023-12-02', 'Bicep Curl', 3, 12, 15, ''),
(8, '2023-12-02', 'Tricep Dip', 3, 10, NULL, 'Bodyweight'),
(9, '2023-12-02', 'Leg Press', 4, 12, 90, ''),
(10, '2023-12-02', 'Lat Pulldown', 3, 10, 45, ''),
(11, '2023-12-02', 'Bench Press', 4, 10, 58, ''),
(12, '2023-12-02', 'Squats', 4, 12, 82.5, ''),
(13, '2023-12-02', 'Deadlift', 3, 8, 102.5, ''),
(14, '2023-12-02', 'Pull-ups', 3, 10, NULL, 'Bodyweight'),
(15, '2023-12-02', 'Overhead Press', 3, 10, 42.5, ''),
(16, '2023-12-03', 'Barbell Row', 3, 10, 52.5, ''),
(17, '2023-12-03', 'Bicep Curl', 3, 12, 17.5, ''),
(18, '2023-12-03', 'Tricep Dip', 3, 10, NULL, 'Bodyweight'),
(19, '2023-12-03', 'Leg Press', 4, 12, 95, ''),
(20, '2023-12-03', 'Lat Pulldown', 3, 10, 47.5, ''),
(21, '2023-12-03', 'Bench Press', 4, 10, 59, ''),
(22, '2023-12-03', 'Squats', 4, 12, 85, ''),
(23, '2023-12-03', 'Deadlift', 3, 8, 105, ''),
(24, '2023-12-03', 'Pull-ups', 3, 10, NULL, 'Bodyweight'),
(25, '2023-12-03', 'Overhead Press', 3, 10, 45, ''),
(26, '2023-12-04', 'Bench Press', 4, 10, 60, ''),
(27, '2023-12-05', 'Bench Press', 4, 10, 62.5, ''),
(28, '2023-12-06', 'Bench Press', 4, 10, 65, ''),
(29, '2023-12-07', 'Bench Press', 4, 10, 67.5, ''),
(30, '2023-12-08', 'Bench Press', 4, 10, 70, ''),
(31, '2023-12-09', 'Bench Press', 4, 10, 72.5, ''),
(32, '2023-12-10', 'Bench Press', 4, 10, 75, ''),
(33, '2023-12-11', 'Bench Press', 4, 10, 77.5, ''),
(34, '2023-12-12', 'Bench Press', 4, 10, 80, ''),
(35, '2023-12-13', 'Bench Press', 4, 10, 82.5, ''),
(36, '2023-12-14', 'Bench Press', 4, 10, 85, ''),
(37, '2023-12-15', 'Bench Press', 4, 10, 87.5, ''),
(38, '2023-12-16', 'Bench Press', 4, 10, 90, ''),
(39, '2023-12-17', 'Bench Press', 4, 10, 92.5, ''),
(40, '2023-12-18', 'Bench Press', 4, 10, 95, ''),
(41, '2023-12-19', 'Bench Press', 4, 10, 97.5, ''),
(42, '2023-12-20', 'Bench Press', 4, 10, 100, ''),
(43, '2023-12-21', 'Bench Press', 4, 10, 102.5, ''),
(44, '2023-12-22', 'Bench Press', 4, 10, 105, ''),
(45, '2023-12-23', 'Bench Press', 4, 10, 107.5, ''),
(46, '2023-12-24', 'Bench Press', 4, 10, 110, ''),
(47, '2023-12-25', 'Bench Press', 4, 10, 112.5, ''),
(48, '2023-12-26', 'Bench Press', 4, 10, 115, ''),
(49, '2023-12-27', 'Bench Press', 4, 10, 117.5, ''),
(50, '2023-12-28', 'Bench Press', 4, 10, 120, '');