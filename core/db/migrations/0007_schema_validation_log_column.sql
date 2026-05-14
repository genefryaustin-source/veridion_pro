

ALTER TABLE schema_validation_log
ADD COLUMN level TEXT;

ALTER TABLE schema_validation_log
ADD COLUMN details_json TEXT;

