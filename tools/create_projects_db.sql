-- Create table
CREATE TABLE IF NOT EXISTS projects (
    id integer PRIMARY KEY,
    name text NOT NULL,
    begin_date text,
    end_date text
);

-- Insert some data into table
INSERT INTO projects (name, begin_date, end_date) VALUES ('Project Name 1', '2023-01-01', '2023-12-31');
INSERT INTO projects (name, begin_date, end_date) VALUES ('Project Name 2', '2023-02-15', '2023-11-20');
INSERT INTO projects (name, begin_date, end_date) VALUES ('Project Name 3', '2023-03-10', '2023-10-05');


