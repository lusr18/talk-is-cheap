-- Create db that only contains user and nutrition info

-- Create user table
CREATE TABLE user (
    id             INTEGER  PRIMARY KEY,
    username       VARCHAR(50) NOT NULL,
    password       VARCHAR(255) NOT NULL,
    email          VARCHAR(255) NOT NULL,
    age            INT NOT NULL,
    gender         INT NOT NULL,            -- 0 male, 1 female, 2 other
    height_cm      INT NOT NULL,             -- cm
    weight_kg      DECIMAL(5,2) NOT NULL    -- kg
);

-- Create nutrition table
CREATE TABLE food (
    id                  INTEGER  PRIMARY KEY,
    user_id             INT,
    food_name           VARCHAR(50) NOT NULL,
    food_date           DATE NOT NULL DEFAULT CURRENT_DATE,
    calories_kcal       INT DEFAULT(0),
    carbohydrates_g     INT DEFAULT(0),    -- grams
    fat_g               INT DEFAULT(0),    -- grams
    protein_g           INT DEFAULT(0),    -- grams
    sodium_mg           INT DEFAULT(0),    -- miligrams
    sugar_g             INT DEFAULT(0),    -- grams
    notes               VARCHAR(255),
    FOREIGN KEY (user_id) REFERENCES user(id)
);

-- Create personal tracker
CREATE TABLE personal_tracker (
    id              INTEGER  PRIMARY KEY,
    user_id         INT,
    record_date     DATE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    height_cm       INT NOT NULL,
    weight_kg       DECIMAL(5,2) NOT NULL,
    body_fat        DECIMAL(5,2) NOT NULL,
    FOREIGN KEY (user_id) REFERENCES user(id)
);

-- Random user data for testing
INSERT INTO user (username, password, email, age, gender, height_cm, weight_kg) VALUES
    ('testuser1', 'password', 'testuser1@email.com', 25, 1, 180, 70);

-- Random personal tracker data for testing
INSERT INTO personal_tracker (user_id, record_date, height_cm, weight_kg, body_fat) VALUES
    (1, '2023-12-01', 180, 80, 20),
    (1, '2023-12-02', 180, 79, 19),
    (1, '2023-12-03', 180, 78, 18),
    (1, '2023-12-04', 180, 77, 17),
    (1, '2023-12-05', 180, 76, 16),
    (1, '2023-12-06', 180, 75, 15),
    (1, '2023-12-07', 180, 74, 14),
    (1, '2023-12-08', 180, 73, 13),
    (1, '2023-12-09', 180, 72, 12),
    (1, '2023-12-10', 180, 71, 11),
    (1, '2023-12-11', 180, 70, 10);

-- Random food data for testing
INSERT INTO food (user_id, food_name, calories_kcal, carbohydrates_g, fat_g, protein_g, sodium_mg, sugar_g) VALUES
    (1, 'Apple', 95, 25, 0.3, 0.5, 2, 19),
    (1, 'Chicken Sandwich', 350, 40, 9, 30, 650, 5),
    (1, 'Bowl of Salad', 150, 10, 7, 5, 200, 4),
    (1, 'Pizza Slice', 285, 36, 10, 12, 640, 3),
    (1, 'Bowl of Oatmeal', 158, 27, 3.2, 5.5, 7, 1);