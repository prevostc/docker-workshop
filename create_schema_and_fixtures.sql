-- noinspection SqlNoDataSourceInspectionForFile
CREATE TABLE call (
  id SERIAL PRIMARY KEY,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  payload TEXT NOT NULL DEFAULT ''
);