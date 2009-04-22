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
