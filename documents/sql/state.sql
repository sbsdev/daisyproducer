-- states
INSERT INTO documents_state (name, sort_order) VALUES ('new', 1);
INSERT INTO documents_state (name, sort_order) VALUES ('scanned', 2);
INSERT INTO documents_state (name, sort_order) VALUES ('ocred', 3);
INSERT INTO documents_state (name, sort_order) VALUES ('marked_up', 4);
INSERT INTO documents_state (name, sort_order) VALUES ('proof_read', 5);
INSERT INTO documents_state (name, sort_order) VALUES ('approved', 6);

-- transitions
-- scanning
INSERT INTO documents_state_next_states (from_state_id, to_state_id) VALUES (1, 2);
-- ocring
INSERT INTO documents_state_next_states (from_state_id, to_state_id) VALUES (2, 3);
-- marking_up
INSERT INTO documents_state_next_states (from_state_id, to_state_id) VALUES (3, 4);
-- proof_reading
INSERT INTO documents_state_next_states (from_state_id, to_state_id) VALUES (4, 5);
-- approving
INSERT INTO documents_state_next_states (from_state_id, to_state_id) VALUES (5, 6);
-- fixing_typos
INSERT INTO documents_state_next_states (from_state_id, to_state_id) VALUES (5, 4);
-- fixing_errata
INSERT INTO documents_state_next_states (from_state_id, to_state_id) VALUES (6, 4);

-- For an initial import it would be nice to have an initial user and
-- a few groups that are responsible for above states 

-- add groups
INSERT INTO auth_group (id, name) VALUES (1, 'Scanners');
INSERT INTO auth_group (id, name) VALUES (2, 'Markers');
INSERT INTO auth_group (id, name) VALUES (3, 'Proof_Readers');
INSERT INTO auth_group (id, name) VALUES (4, 'Approvers');

-- add a demo user
-- is unfortunately backend specific and therefore handled in state.*.sql

-- add groups to demo user
INSERT INTO auth_user_groups (id, user_id, group_id) VALUES (1, 2, 1);
INSERT INTO auth_user_groups (id, user_id, group_id) VALUES (2, 2, 2);
INSERT INTO auth_user_groups (id, user_id, group_id) VALUES (3, 2, 3);
INSERT INTO auth_user_groups (id, user_id, group_id) VALUES (4, 2, 4);

-- now make sure the groups are responsible for their state
-- Scanners are responsible for new and scanned documents, i.e. they
-- should do scanning and OCR
INSERT INTO documents_state_responsible (id, state_id, group_id) VALUES (1, 1, 1);
INSERT INTO documents_state_responsible (id, state_id, group_id) VALUES (2, 2, 1);
-- Markers are responsible for ocred documents, i.e. they should do
-- markup 
INSERT INTO documents_state_responsible (id, state_id, group_id) VALUES (3, 3, 2);
-- Proof_Readers are responsible for marked_up documents, i.e. they
-- should do proof reading
INSERT INTO documents_state_responsible (id, state_id, group_id) VALUES (4, 4, 3);
-- Approvers are responsible for proof_read and approved documents
INSERT INTO documents_state_responsible (id, state_id, group_id) VALUES (5, 5, 4);
INSERT INTO documents_state_responsible (id, state_id, group_id) VALUES (6, 6, 4);
