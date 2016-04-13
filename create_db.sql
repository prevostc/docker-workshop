-- noinspection SqlNoDataSourceInspectionForFile
CREATE USER dockerworkshop WITH ENCRYPTED PASSWORD 'dockerworkshop' SUPERUSER;
CREATE DATABASE dockerworkshop WITH OWNER dockerworkshop;