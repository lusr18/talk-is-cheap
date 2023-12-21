-- Create db
-- CREATE DATABASE workout_tracker;


-- Create user table
CREATE TABLE user (
    id             INTEGER  PRIMARY KEY,
    username       VARCHAR(50) NOT NULL,
    password       VARCHAR(255) NOT NULL,
    email          VARCHAR(255) NOT NULL,
    age            INT NOT NULL,
    gender         INT NOT NULL,    -- 0 male, 1 female, 2 other
    height         INT NOT NULL    -- cm
);

-- Create exercise table
CREATE TABLE exercise (
    id              INTEGER  PRIMARY KEY,
    user_id         INT,
    exercise_name   VARCHAR(50) NOT NULL,
    exercise_date   DATE NOT NULL DEFAULT CURRENT_DATE,
    -- exercise_time   TIME NOT NULL DEFAULT CURRENT_TIME,
    exercise_type   VARCHAR(50) NOT NULL,
    sets            INT DEFAULT(0),
    reps            INT DEFAULT(0),
    weight          DECIMAL(5,2) DEFAULT(0), -- Weight in kg
    duration        DECIMAL(5,2) DEFAULT(0), -- Duration in minutes
    notes           VARCHAR(255),
    FOREIGN KEY (user_id) REFERENCES user(id)
);

--Create exercise routine
CREATE TABLE exercise_routine (
    id             INTEGER PRIMARY KEY,
    routine_name   VARCHAR(255) NOT NULL,
    routine_plan   VARCHAR(255) NOT NULL
);

-- Create nutrition table
CREATE TABLE food (
    id             INTEGER  PRIMARY KEY,
    user_id        INT,
    food_name      VARCHAR(50) NOT NULL,
    food_date      DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    calories       INT DEFAULT(0),
    carbohydrates  INT DEFAULT(0),    -- grams
    fat            INT DEFAULT(0),    -- grams
    protein        INT DEFAULT(0),    -- grams
    sodium         INT DEFAULT(0),    -- miligrams
    sugar          INT DEFAULT(0),    -- grams
    notes          VARCHAR(255),
    FOREIGN KEY (user_id) REFERENCES user(id)
);

-- Create personal tracker
CREATE TABLE personal_tracker (
    id              INTEGER  PRIMARY KEY,
    user_id         INT,
    record_date     DATE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    weight          DECIMAL(5,2) NOT NULL,
    body_fat        DECIMAL(5,2) NOT NULL,
    FOREIGN KEY (user_id) REFERENCES user(id)
);


-- Random user data for testing
INSERT INTO user (username, password, email, age, gender, height) VALUES
    ('testuser1', 'password', 'testuser1@email.com', 25, 1, 180);

-- Random personal tracker data for testing
INSERT INTO personal_tracker (user_id, record_date, weight, body_fat) VALUES
    (1, '2023-12-01', 80, 20),
    (1, '2023-12-02', 79, 19),
    (1, '2023-12-03', 78, 18),
    (1, '2023-12-04', 77, 17),
    (1, '2023-12-05', 76, 16),
    (1, '2023-12-06', 75, 15),
    (1, '2023-12-07', 74, 14),
    (1, '2023-12-08', 73, 13),
    (1, '2023-12-09', 72, 12),
    (1, '2023-12-10', 71, 11),
    (1, '2023-12-11', 70, 10);

-- Random food data for testing
INSERT INTO food (user_id, food_name, calories, carbohydrates, fat, protein, sodium, sugar) VALUES
    (1, 'Apple', 95, 25, 0.3, 0.5, 2, 19),
    (1, 'Chicken Sandwich', 350, 40, 9, 30, 650, 5),
    (1, 'Bowl of Salad', 150, 10, 7, 5, 200, 4),
    (1, 'Pizza Slice', 285, 36, 10, 12, 640, 3),
    (1, 'Bowl of Oatmeal', 158, 27, 3.2, 5.5, 7, 1);

-- -- Random workout data for testing
INSERT INTO exercise (user_id, exercise_date, exercise_name, exercise_type, sets, reps, weight, duration) VALUES
-- 2023-01-01 (Leg Day)
(1, '2023-01-01', 'Bench Press', 'Weightlifting', 3, 10, 60, 30),
(1, '2023-01-01', 'Squat', 'Weightlifting', 3, 10, 80, 30),
(1, '2023-01-01', 'Deadlift', 'Weightlifting', 3, 10, 100, 30),

-- 2023-01-04 (Chest Day)
(1, '2023-01-04', 'Bench Press', 'Weightlifting', 3, 12, 62.5, 30),
(1, '2023-01-04', 'Incline Dumbbell Press', 'Weightlifting', 3, 12, 30, 30),
(1, '2023-01-04', 'Chest Fly', 'Weightlifting', 3, 12, 15, 30),

-- 2023-01-07 (Pull Day)
(1, '2023-01-07', 'Pull-ups', 'Weightlifting', 3, 10, 0, 30),
(1, '2023-01-07', 'Bent Over Rows', 'Weightlifting', 3, 10, 55, 30),
(1, '2023-01-07', 'Lat Pulldowns', 'Weightlifting', 3, 10, 50, 30),

-- 2023-01-11 (Chest Day)
(1, '2023-01-11', 'Bench Press', 'Weightlifting', 3, 12, 65, 30),
(1, '2023-01-11', 'Incline Dumbbell Press', 'Weightlifting', 3, 12, 32.5, 30),
(1, '2023-01-11', 'Chest Fly', 'Weightlifting', 3, 12, 17.5, 30),

-- 2023-01-14 (Leg Day)
(1, '2023-01-14', 'Bench Press', 'Weightlifting', 3, 10, 62.5, 30),
(1, '2023-01-14', 'Squat', 'Weightlifting', 3, 10, 82.5, 30),
(1, '2023-01-14', 'Deadlift', 'Weightlifting', 3, 10, 102.5, 30),

-- 2023-01-17 (Pull Day)
(1, '2023-01-17', 'Pull-ups', 'Weightlifting', 3, 10, 0, 30),
(1, '2023-01-17', 'Bent Over Rows', 'Weightlifting', 3, 10, 57.5, 30),
(1, '2023-01-17', 'Lat Pulldowns', 'Weightlifting', 3, 10, 52.5, 30);



-- Random Workout Routine Data for testing
INSERT INTO exercise_routine (routine_name, routine_plan) VALUES
    ('Chris Heria 100 Pushups', '1. Regular Pushups, 10 Reps\n2. Wide Pushups, 10 Reps\n3. Diamond Pushups, 10 Reps\n4. Explosive Pushups, 10 Reps\n5. Side-to-Side Pushups, 10 Reps\n6. Clapping Pushups, 10 Reps\n7. Archer Pushups, 10 Reps\n8. Open and Close Pushups, 10 Reps\n9. Typewriter Pushups\n10. Pushup + Shoulder Tap\nNotes: 3 or more sets.'),
    ('Chris Heria 100 Pullups', '1. Pull-ups, 10 Reps\n2. Chin-ups, 10 Reps\n3. Switching one arm chin up hold, 10 Reps\n4. Close grip pull-ups, 10 Reps\n5. Close grip chin ups, 10 Reps\n6. Pull ups open & closed, 10 Reps\n7. Commando Pull-ups, 10 Reps\n8. Half Pull-ups, 10 Reps\nNotes: 3 or more sets.'),
    ('Chris Heria Complete 20 Min Full Body Workout', '1. Renegade Rows, 45 Secs\n2. Wide Rows, 45 Secs\n3. Reverse Leg Raises, 45 Secs\n4. Staggered Romanian Deadlift, 45 Secs\n5. Goblet Squat Calf Raises, 45 Secs\n6. Thrusters, 45 Secs\n7. Rear Delt Flys with Skis, 45 Secs\n8. Pike Push Ups, 45 Secs\n9. Bench Dips, 45 Secs\n10. Push Ups, 45 Secs\n11. Elevated Diamond Squeeze Push Ups, 45 Secs\n12. Skull Crushers, 45 Secs\n13. Dumbell Kick Backs, 45 Secs\n14. Bicep + Hammer Curls, 45 Secs\n15. Russian Twist, 45 Secs\n16. Reach Ups, 45 Secs\n17. Mountain Climbers, 45 Secs\nNotes: 45 Sec workout, 15 Sec rest.');




