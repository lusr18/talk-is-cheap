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
    exercise_date   DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    exercise_type   VARCHAR(50) NOT NULL,
    sets            INT DEFAULT(0),
    reps            INT DEFAULT(0),
    weight          DECIMAL(5,2) DEFAULT(0), -- Weight in kg
    duration        DECIMAL(5,2) DEFAULT(0), -- Duration in minutes
    notes           VARCHAR(255),
    FOREIGN KEY (user_id) REFERENCES user(id)
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

-- -- Create personal tracker
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
(1, '2023-01-01 08:00:00', 'Bench Press', 'Weightlifting', 3, 10, 60, 30),
(1, '2023-01-01 08:30:00', 'Squat', 'Weightlifting', 3, 10, 80, 30),
(1, '2023-01-01 09:00:00', 'Deadlift', 'Weightlifting', 3, 10, 100, 30),

-- 2023-01-04 (Chest Day)
(1, '2023-01-04 08:00:00', 'Bench Press', 'Weightlifting', 3, 12, 62.5, 30),
(1, '2023-01-04 08:30:00', 'Incline Dumbbell Press', 'Weightlifting', 3, 12, 30, 30),
(1, '2023-01-04 09:00:00', 'Chest Fly', 'Weightlifting', 3, 12, 15, 30),

-- 2023-01-07 (Pull Day)
(1, '2023-01-07 08:00:00', 'Pull-ups', 'Weightlifting', 3, 10, 0, 30),
(1, '2023-01-07 08:30:00', 'Bent Over Rows', 'Weightlifting', 3, 10, 55, 30),
(1, '2023-01-07 09:00:00', 'Lat Pulldowns', 'Weightlifting', 3, 10, 50, 30),

-- 2023-01-11 (Chest Day)
(1, '2023-01-11 08:00:00', 'Bench Press', 'Weightlifting', 3, 12, 65, 30),
(1, '2023-01-11 08:30:00', 'Incline Dumbbell Press', 'Weightlifting', 3, 12, 32.5, 30),
(1, '2023-01-11 09:00:00', 'Chest Fly', 'Weightlifting', 3, 12, 17.5, 30),

-- 2023-01-14 (Leg Day)
(1, '2023-01-14 08:00:00', 'Bench Press', 'Weightlifting', 3, 10, 62.5, 30),
(1, '2023-01-14 08:30:00', 'Squat', 'Weightlifting', 3, 10, 82.5, 30),
(1, '2023-01-14 09:00:00', 'Deadlift', 'Weightlifting', 3, 10, 102.5, 30),

-- 2023-01-17 (Pull Day)
(1, '2023-01-17 08:00:00', 'Pull-ups', 'Weightlifting', 3, 10, 0, 30),
(1, '2023-01-17 08:30:00', 'Bent Over Rows', 'Weightlifting', 3, 10, 57.5, 30),
(1, '2023-01-17 09:00:00', 'Lat Pulldowns', 'Weightlifting', 3, 10, 52.5, 30);
