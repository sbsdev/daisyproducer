-- add a demo user
INSERT INTO auth_user (id, username, first_name, last_name, email, password,
       is_staff, is_active, is_superuser, last_login, date_joined) 
VALUES (2, 'demo', 'Demo', 'User', 'demo.user@example.com', 'sha1$7f00f$139ae061147ffafd825cfec2951d86e787959aef', 0, 1, 0, '2009-11-26 16:23:51.949691','2009-11-26 16:23:37.074040');
