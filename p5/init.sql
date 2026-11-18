CREATE TABLE IF NOT EXISTS students (
  id INT AUTO_INCREMENT PRIMARY KEY,
  name VARCHAR(50),
  course VARCHAR(50)
);
INSERT INTO students (name, course) VALUES
  ('Arvind', 'DevOps'),
  ('Priya', 'Data Science'),
  ('Rahul', 'Cloud Computing');
