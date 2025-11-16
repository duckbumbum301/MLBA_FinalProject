-- Update password hash cho 3 demo users
-- Password: "123"
-- Hash mới (verified): $2b$12$3jGm14C9GlOONZhCsAHhPuQmGja08lPvreGq3SQWQiGRYSMXbcsLm

UPDATE `user` 
SET `password_hash` = '$2b$12$3jGm14C9GlOONZhCsAHhPuQmGja08lPvreGq3SQWQiGRYSMXbcsLm'
WHERE `username` IN ('babyshark', 'fathershark', 'momshark');

SELECT id, username, role, 'Password updated to: 123' as status FROM `user`;
