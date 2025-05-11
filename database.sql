CREATE DATABASE student_info_system;
USE student_info_system;

CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    name VARCHAR(255) NOT NULL,
    role ENUM('student', 'teacher') NOT NULL,
    department VARCHAR(50) NOT NULL,
    year_of_joining INT
);


CREATE TABLE marks (
    student_id INT,
    semester INT,
    marks INT,
    attendance INT,
    PRIMARY KEY (student_id, semester),
    FOREIGN KEY (student_id) REFERENCES users(id)
);


CREATE TABLE notifications (
    id INT AUTO_INCREMENT PRIMARY KEY,
    student_id INT,
    teacher_id INT,
    semester INT,
    message TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (student_id) REFERENCES users(id),
    FOREIGN KEY (teacher_id) REFERENCES users(id)
);
