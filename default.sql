--
-- PostgreSQL database cluster dump
--

SET default_transaction_read_only = off;

SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;

--
-- Drop databases (except postgres and template1)
--

DROP DATABASE pg;




--
-- Drop roles
--

DROP ROLE "user";


--
-- Roles
--

CREATE ROLE "user";
ALTER ROLE "user" WITH SUPERUSER INHERIT CREATEROLE CREATEDB LOGIN REPLICATION BYPASSRLS PASSWORD 'SCRAM-SHA-256$4096:86eBkKfwp/xbGbIAHwt+Pw==$q4vC0uQYv9uFoXgx95pi6GfzroA00rFRrFj3cEoWwxY=:3EhBgyZgR3H+y+5PGsmWwl2xu7oq++LeLQKNP+lG5oE=';

--
-- User Configurations
--








--
-- Databases
--

--
-- Database "template1" dump
--

--
-- PostgreSQL database dump
--

-- Dumped from database version 16.3 (Debian 16.3-1.pgdg120+1)
-- Dumped by pg_dump version 16.3 (Debian 16.3-1.pgdg120+1)

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

UPDATE pg_catalog.pg_database SET datistemplate = false WHERE datname = 'template1';
DROP DATABASE template1;
--
-- Name: template1; Type: DATABASE; Schema: -; Owner: user
--

CREATE DATABASE template1 WITH TEMPLATE = template0 ENCODING = 'UTF8' LOCALE_PROVIDER = libc LOCALE = 'en_US.utf8';


ALTER DATABASE template1 OWNER TO "user";

\connect template1

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- Name: DATABASE template1; Type: COMMENT; Schema: -; Owner: user
--

COMMENT ON DATABASE template1 IS 'default template for new databases';


--
-- Name: template1; Type: DATABASE PROPERTIES; Schema: -; Owner: user
--

ALTER DATABASE template1 IS_TEMPLATE = true;


\connect template1

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- Name: DATABASE template1; Type: ACL; Schema: -; Owner: user
--

REVOKE CONNECT,TEMPORARY ON DATABASE template1 FROM PUBLIC;
GRANT CONNECT ON DATABASE template1 TO PUBLIC;


--
-- PostgreSQL database dump complete
--

--
-- Database "pg" dump
--

--
-- PostgreSQL database dump
--

-- Dumped from database version 16.3 (Debian 16.3-1.pgdg120+1)
-- Dumped by pg_dump version 16.3 (Debian 16.3-1.pgdg120+1)

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- Name: pg; Type: DATABASE; Schema: -; Owner: user
--

CREATE DATABASE pg WITH TEMPLATE = template0 ENCODING = 'UTF8' LOCALE_PROVIDER = libc LOCALE = 'en_US.utf8';


ALTER DATABASE pg OWNER TO "user";

\connect pg

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- PostgreSQL database dump complete
--

--
-- Database "postgres" dump
--

--
-- PostgreSQL database dump
--

-- Dumped from database version 16.3 (Debian 16.3-1.pgdg120+1)
-- Dumped by pg_dump version 16.3 (Debian 16.3-1.pgdg120+1)

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

DROP DATABASE postgres;
--
-- Name: postgres; Type: DATABASE; Schema: -; Owner: user
--

CREATE DATABASE postgres WITH TEMPLATE = template0 ENCODING = 'UTF8' LOCALE_PROVIDER = libc LOCALE = 'en_US.utf8';


ALTER DATABASE postgres OWNER TO "user";

\connect postgres

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- Name: DATABASE postgres; Type: COMMENT; Schema: -; Owner: user
--

COMMENT ON DATABASE postgres IS 'default administrative connection database';


SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: about_sleep_template; Type: TABLE; Schema: public; Owner: user
--

CREATE TABLE public.about_sleep_template (
    id integer NOT NULL,
    name character varying NOT NULL,
    text character varying NOT NULL,
    is_archived boolean NOT NULL
);


ALTER TABLE public.about_sleep_template OWNER TO "user";

--
-- Name: about_sleep_template_id_seq; Type: SEQUENCE; Schema: public; Owner: user
--

CREATE SEQUENCE public.about_sleep_template_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.about_sleep_template_id_seq OWNER TO "user";

--
-- Name: about_sleep_template_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: user
--

ALTER SEQUENCE public.about_sleep_template_id_seq OWNED BY public.about_sleep_template.id;


--
-- Name: access_group; Type: TABLE; Schema: public; Owner: user
--

CREATE TABLE public.access_group (
    id integer NOT NULL,
    name character varying NOT NULL,
    is_archived boolean NOT NULL,
    app_id integer
);


ALTER TABLE public.access_group OWNER TO "user";

--
-- Name: access_group_id_seq; Type: SEQUENCE; Schema: public; Owner: user
--

CREATE SEQUENCE public.access_group_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.access_group_id_seq OWNER TO "user";

--
-- Name: access_group_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: user
--

ALTER SEQUENCE public.access_group_id_seq OWNED BY public.access_group.id;


--
-- Name: account; Type: TABLE; Schema: public; Owner: user
--

CREATE TABLE public.account (
    id integer NOT NULL,
    public_id character varying NOT NULL,
    created_on timestamp without time zone NOT NULL,
    last_login timestamp without time zone,
    first_name character varying NOT NULL,
    last_name character varying NOT NULL,
    email character varying NOT NULL,
    phone_number character varying,
    is_confirmed boolean NOT NULL,
    is_archived boolean NOT NULL,
    _password character varying NOT NULL
);


ALTER TABLE public.account OWNER TO "user";

--
-- Name: account_id_seq; Type: SEQUENCE; Schema: public; Owner: user
--

CREATE SEQUENCE public.account_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.account_id_seq OWNER TO "user";

--
-- Name: account_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: user
--

ALTER SEQUENCE public.account_id_seq OWNED BY public.account.id;


--
-- Name: action; Type: TABLE; Schema: public; Owner: user
--

CREATE TABLE public.action (
    id integer NOT NULL,
    value character varying NOT NULL
);


ALTER TABLE public.action OWNER TO "user";

--
-- Name: action_id_seq; Type: SEQUENCE; Schema: public; Owner: user
--

CREATE SEQUENCE public.action_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.action_id_seq OWNER TO "user";

--
-- Name: action_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: user
--

ALTER SEQUENCE public.action_id_seq OWNED BY public.action.id;


--
-- Name: app; Type: TABLE; Schema: public; Owner: user
--

CREATE TABLE public.app (
    id integer NOT NULL,
    name character varying NOT NULL
);


ALTER TABLE public.app OWNER TO "user";

--
-- Name: app_id_seq; Type: SEQUENCE; Schema: public; Owner: user
--

CREATE SEQUENCE public.app_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.app_id_seq OWNER TO "user";

--
-- Name: app_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: user
--

ALTER SEQUENCE public.app_id_seq OWNED BY public.app.id;


--
-- Name: blocked_token; Type: TABLE; Schema: public; Owner: user
--

CREATE TABLE public.blocked_token (
    id integer NOT NULL,
    jti character varying NOT NULL,
    created_on timestamp without time zone NOT NULL
);


ALTER TABLE public.blocked_token OWNER TO "user";

--
-- Name: blocked_token_id_seq; Type: SEQUENCE; Schema: public; Owner: user
--

CREATE SEQUENCE public.blocked_token_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.blocked_token_id_seq OWNER TO "user";

--
-- Name: blocked_token_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: user
--

ALTER SEQUENCE public.blocked_token_id_seq OWNED BY public.blocked_token.id;


--
-- Name: join_access_group_permission; Type: TABLE; Schema: public; Owner: user
--

CREATE TABLE public.join_access_group_permission (
    access_group_id integer NOT NULL,
    permission_id integer NOT NULL
);


ALTER TABLE public.join_access_group_permission OWNER TO "user";

--
-- Name: join_account_access_group; Type: TABLE; Schema: public; Owner: user
--

CREATE TABLE public.join_account_access_group (
    account_id integer NOT NULL,
    access_group_id integer NOT NULL
);


ALTER TABLE public.join_account_access_group OWNER TO "user";

--
-- Name: join_account_study; Type: TABLE; Schema: public; Owner: user
--

CREATE TABLE public.join_account_study (
    account_id integer NOT NULL,
    study_id integer NOT NULL,
    role_id integer NOT NULL
);


ALTER TABLE public.join_account_study OWNER TO "user";

--
-- Name: join_role_permission; Type: TABLE; Schema: public; Owner: user
--

CREATE TABLE public.join_role_permission (
    role_id integer NOT NULL,
    permission_id integer NOT NULL
);


ALTER TABLE public.join_role_permission OWNER TO "user";

--
-- Name: join_study_role; Type: TABLE; Schema: public; Owner: user
--

CREATE TABLE public.join_study_role (
    study_id integer NOT NULL,
    role_id integer NOT NULL
);


ALTER TABLE public.join_study_role OWNER TO "user";

--
-- Name: permission; Type: TABLE; Schema: public; Owner: user
--

CREATE TABLE public.permission (
    id integer NOT NULL,
    _action_id integer,
    _resource_id integer
);


ALTER TABLE public.permission OWNER TO "user";

--
-- Name: permission_id_seq; Type: SEQUENCE; Schema: public; Owner: user
--

CREATE SEQUENCE public.permission_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.permission_id_seq OWNER TO "user";

--
-- Name: permission_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: user
--

ALTER SEQUENCE public.permission_id_seq OWNED BY public.permission.id;


--
-- Name: resource; Type: TABLE; Schema: public; Owner: user
--

CREATE TABLE public.resource (
    id integer NOT NULL,
    value character varying NOT NULL
);


ALTER TABLE public.resource OWNER TO "user";

--
-- Name: resource_id_seq; Type: SEQUENCE; Schema: public; Owner: user
--

CREATE SEQUENCE public.resource_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.resource_id_seq OWNER TO "user";

--
-- Name: resource_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: user
--

ALTER SEQUENCE public.resource_id_seq OWNED BY public.resource.id;


--
-- Name: role; Type: TABLE; Schema: public; Owner: user
--

CREATE TABLE public.role (
    id integer NOT NULL,
    name character varying NOT NULL,
    is_archived boolean NOT NULL
);


ALTER TABLE public.role OWNER TO "user";

--
-- Name: role_id_seq; Type: SEQUENCE; Schema: public; Owner: user
--

CREATE SEQUENCE public.role_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.role_id_seq OWNER TO "user";

--
-- Name: role_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: user
--

ALTER SEQUENCE public.role_id_seq OWNED BY public.role.id;


--
-- Name: study; Type: TABLE; Schema: public; Owner: user
--

CREATE TABLE public.study (
    id integer NOT NULL,
    name character varying NOT NULL,
    acronym character varying NOT NULL,
    ditti_id character varying NOT NULL,
    email character varying NOT NULL,
    is_archived boolean NOT NULL
);


ALTER TABLE public.study OWNER TO "user";

--
-- Name: study_id_seq; Type: SEQUENCE; Schema: public; Owner: user
--

CREATE SEQUENCE public.study_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.study_id_seq OWNER TO "user";

--
-- Name: study_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: user
--

ALTER SEQUENCE public.study_id_seq OWNED BY public.study.id;


--
-- Name: about_sleep_template id; Type: DEFAULT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.about_sleep_template ALTER COLUMN id SET DEFAULT nextval('public.about_sleep_template_id_seq'::regclass);


--
-- Name: access_group id; Type: DEFAULT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.access_group ALTER COLUMN id SET DEFAULT nextval('public.access_group_id_seq'::regclass);


--
-- Name: account id; Type: DEFAULT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.account ALTER COLUMN id SET DEFAULT nextval('public.account_id_seq'::regclass);


--
-- Name: action id; Type: DEFAULT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.action ALTER COLUMN id SET DEFAULT nextval('public.action_id_seq'::regclass);


--
-- Name: app id; Type: DEFAULT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.app ALTER COLUMN id SET DEFAULT nextval('public.app_id_seq'::regclass);


--
-- Name: blocked_token id; Type: DEFAULT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.blocked_token ALTER COLUMN id SET DEFAULT nextval('public.blocked_token_id_seq'::regclass);


--
-- Name: permission id; Type: DEFAULT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.permission ALTER COLUMN id SET DEFAULT nextval('public.permission_id_seq'::regclass);


--
-- Name: resource id; Type: DEFAULT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.resource ALTER COLUMN id SET DEFAULT nextval('public.resource_id_seq'::regclass);


--
-- Name: role id; Type: DEFAULT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.role ALTER COLUMN id SET DEFAULT nextval('public.role_id_seq'::regclass);


--
-- Name: study id; Type: DEFAULT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.study ALTER COLUMN id SET DEFAULT nextval('public.study_id_seq'::regclass);


--
-- Data for Name: about_sleep_template; Type: TABLE DATA; Schema: public; Owner: user
--

COPY public.about_sleep_template (id, name, text, is_archived) FROM stdin;
\.


--
-- Data for Name: access_group; Type: TABLE DATA; Schema: public; Owner: user
--

COPY public.access_group (id, name, is_archived, app_id) FROM stdin;
1	Admin	f	1
2	Ditti Admin	f	2
\.


--
-- Data for Name: account; Type: TABLE DATA; Schema: public; Owner: user
--

COPY public.account (id, public_id, created_on, last_login, first_name, last_name, email, phone_number, is_confirmed, is_archived, _password) FROM stdin;
\.


--
-- Data for Name: action; Type: TABLE DATA; Schema: public; Owner: user
--

COPY public.action (id, value) FROM stdin;
1	*
2	View
3	Create
4	Edit
5	Archive
6	Delete
\.


--
-- Data for Name: app; Type: TABLE DATA; Schema: public; Owner: user
--

COPY public.app (id, name) FROM stdin;
1	Admin Dashboard
2	Ditti App Dashboard
\.


--
-- Data for Name: blocked_token; Type: TABLE DATA; Schema: public; Owner: user
--

COPY public.blocked_token (id, jti, created_on) FROM stdin;
\.


--
-- Data for Name: join_access_group_permission; Type: TABLE DATA; Schema: public; Owner: user
--

COPY public.join_access_group_permission (access_group_id, permission_id) FROM stdin;
1	2
1	1
2	3
2	4
2	1
\.


--
-- Data for Name: join_account_access_group; Type: TABLE DATA; Schema: public; Owner: user
--

COPY public.join_account_access_group (account_id, access_group_id) FROM stdin;
\.


--
-- Data for Name: join_account_study; Type: TABLE DATA; Schema: public; Owner: user
--

COPY public.join_account_study (account_id, study_id, role_id) FROM stdin;
\.


--
-- Data for Name: join_role_permission; Type: TABLE DATA; Schema: public; Owner: user
--

COPY public.join_role_permission (role_id, permission_id) FROM stdin;
\.


--
-- Data for Name: join_study_role; Type: TABLE DATA; Schema: public; Owner: user
--

COPY public.join_study_role (study_id, role_id) FROM stdin;
\.


--
-- Data for Name: permission; Type: TABLE DATA; Schema: public; Owner: user
--

COPY public.permission (id, _action_id, _resource_id) FROM stdin;
1	1	1
2	2	2
3	2	3
4	2	4
\.


--
-- Data for Name: resource; Type: TABLE DATA; Schema: public; Owner: user
--

COPY public.resource (id, value) FROM stdin;
1	*
2	Admin Dashboard
3	Ditti App Dashboard
4	All Studies
5	Users
6	Accounts
7	Studies
8	Roles
9	Access Groups
10	Audio File
\.


--
-- Data for Name: role; Type: TABLE DATA; Schema: public; Owner: user
--

COPY public.role (id, name, is_archived) FROM stdin;
\.


--
-- Data for Name: study; Type: TABLE DATA; Schema: public; Owner: user
--

COPY public.study (id, name, acronym, ditti_id, email, is_archived) FROM stdin;
\.


--
-- Name: about_sleep_template_id_seq; Type: SEQUENCE SET; Schema: public; Owner: user
--

SELECT pg_catalog.setval('public.about_sleep_template_id_seq', 1, true);


--
-- Name: access_group_id_seq; Type: SEQUENCE SET; Schema: public; Owner: user
--

SELECT pg_catalog.setval('public.access_group_id_seq', 1, true);


--
-- Name: account_id_seq; Type: SEQUENCE SET; Schema: public; Owner: user
--

SELECT pg_catalog.setval('public.account_id_seq', 2, true);


--
-- Name: action_id_seq; Type: SEQUENCE SET; Schema: public; Owner: user
--

SELECT pg_catalog.setval('public.action_id_seq', 6, true);


--
-- Name: app_id_seq; Type: SEQUENCE SET; Schema: public; Owner: user
--

SELECT pg_catalog.setval('public.app_id_seq', 1, true);


--
-- Name: blocked_token_id_seq; Type: SEQUENCE SET; Schema: public; Owner: user
--

SELECT pg_catalog.setval('public.blocked_token_id_seq', 1, false);


--
-- Name: permission_id_seq; Type: SEQUENCE SET; Schema: public; Owner: user
--

SELECT pg_catalog.setval('public.permission_id_seq', 4, true);


--
-- Name: resource_id_seq; Type: SEQUENCE SET; Schema: public; Owner: user
--

SELECT pg_catalog.setval('public.resource_id_seq', 10, true);


--
-- Name: role_id_seq; Type: SEQUENCE SET; Schema: public; Owner: user
--

SELECT pg_catalog.setval('public.role_id_seq', 1, false);


--
-- Name: study_id_seq; Type: SEQUENCE SET; Schema: public; Owner: user
--

SELECT pg_catalog.setval('public.study_id_seq', 1, false);


--
-- Name: about_sleep_template about_sleep_template_name_key; Type: CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.about_sleep_template
    ADD CONSTRAINT about_sleep_template_name_key UNIQUE (name);


--
-- Name: about_sleep_template about_sleep_template_pkey; Type: CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.about_sleep_template
    ADD CONSTRAINT about_sleep_template_pkey PRIMARY KEY (id);


--
-- Name: access_group access_group_name_key; Type: CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.access_group
    ADD CONSTRAINT access_group_name_key UNIQUE (name);


--
-- Name: access_group access_group_pkey; Type: CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.access_group
    ADD CONSTRAINT access_group_pkey PRIMARY KEY (id);


--
-- Name: account account_email_key; Type: CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.account
    ADD CONSTRAINT account_email_key UNIQUE (email);


--
-- Name: account account_phone_number_key; Type: CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.account
    ADD CONSTRAINT account_phone_number_key UNIQUE (phone_number);


--
-- Name: account account_pkey; Type: CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.account
    ADD CONSTRAINT account_pkey PRIMARY KEY (id);


--
-- Name: account account_public_id_key; Type: CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.account
    ADD CONSTRAINT account_public_id_key UNIQUE (public_id);


--
-- Name: action action_pkey; Type: CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.action
    ADD CONSTRAINT action_pkey PRIMARY KEY (id);


--
-- Name: action action_value_key; Type: CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.action
    ADD CONSTRAINT action_value_key UNIQUE (value);


--
-- Name: app app_name_key; Type: CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.app
    ADD CONSTRAINT app_name_key UNIQUE (name);


--
-- Name: app app_pkey; Type: CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.app
    ADD CONSTRAINT app_pkey PRIMARY KEY (id);


--
-- Name: blocked_token blocked_token_pkey; Type: CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.blocked_token
    ADD CONSTRAINT blocked_token_pkey PRIMARY KEY (id);


--
-- Name: join_access_group_permission join_access_group_permission_pkey; Type: CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.join_access_group_permission
    ADD CONSTRAINT join_access_group_permission_pkey PRIMARY KEY (access_group_id, permission_id);


--
-- Name: join_account_access_group join_account_access_group_pkey; Type: CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.join_account_access_group
    ADD CONSTRAINT join_account_access_group_pkey PRIMARY KEY (account_id, access_group_id);


--
-- Name: join_account_study join_account_study_pkey; Type: CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.join_account_study
    ADD CONSTRAINT join_account_study_pkey PRIMARY KEY (account_id, study_id);


--
-- Name: join_role_permission join_role_permission_pkey; Type: CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.join_role_permission
    ADD CONSTRAINT join_role_permission_pkey PRIMARY KEY (role_id, permission_id);


--
-- Name: join_study_role join_study_role_pkey; Type: CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.join_study_role
    ADD CONSTRAINT join_study_role_pkey PRIMARY KEY (study_id, role_id);


--
-- Name: permission permission__action_id__resource_id_key; Type: CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.permission
    ADD CONSTRAINT permission__action_id__resource_id_key UNIQUE (_action_id, _resource_id);


--
-- Name: permission permission_pkey; Type: CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.permission
    ADD CONSTRAINT permission_pkey PRIMARY KEY (id);


--
-- Name: resource resource_pkey; Type: CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.resource
    ADD CONSTRAINT resource_pkey PRIMARY KEY (id);


--
-- Name: resource resource_value_key; Type: CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.resource
    ADD CONSTRAINT resource_value_key UNIQUE (value);


--
-- Name: role role_pkey; Type: CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.role
    ADD CONSTRAINT role_pkey PRIMARY KEY (id);


--
-- Name: study study_acronym_key; Type: CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.study
    ADD CONSTRAINT study_acronym_key UNIQUE (acronym);


--
-- Name: study study_ditti_id_key; Type: CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.study
    ADD CONSTRAINT study_ditti_id_key UNIQUE (ditti_id);


--
-- Name: study study_name_key; Type: CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.study
    ADD CONSTRAINT study_name_key UNIQUE (name);


--
-- Name: study study_pkey; Type: CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.study
    ADD CONSTRAINT study_pkey PRIMARY KEY (id);


--
-- Name: access_group access_group_app_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.access_group
    ADD CONSTRAINT access_group_app_id_fkey FOREIGN KEY (app_id) REFERENCES public.app(id) ON DELETE CASCADE;


--
-- Name: join_access_group_permission join_access_group_permission_access_group_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.join_access_group_permission
    ADD CONSTRAINT join_access_group_permission_access_group_id_fkey FOREIGN KEY (access_group_id) REFERENCES public.access_group(id) ON DELETE CASCADE;


--
-- Name: join_access_group_permission join_access_group_permission_permission_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.join_access_group_permission
    ADD CONSTRAINT join_access_group_permission_permission_id_fkey FOREIGN KEY (permission_id) REFERENCES public.permission(id) ON DELETE CASCADE;


--
-- Name: join_account_access_group join_account_access_group_access_group_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.join_account_access_group
    ADD CONSTRAINT join_account_access_group_access_group_id_fkey FOREIGN KEY (access_group_id) REFERENCES public.access_group(id) ON DELETE CASCADE;


--
-- Name: join_account_access_group join_account_access_group_account_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.join_account_access_group
    ADD CONSTRAINT join_account_access_group_account_id_fkey FOREIGN KEY (account_id) REFERENCES public.account(id);


--
-- Name: join_account_study join_account_study_account_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.join_account_study
    ADD CONSTRAINT join_account_study_account_id_fkey FOREIGN KEY (account_id) REFERENCES public.account(id);


--
-- Name: join_account_study join_account_study_role_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.join_account_study
    ADD CONSTRAINT join_account_study_role_id_fkey FOREIGN KEY (role_id) REFERENCES public.role(id) ON DELETE CASCADE;


--
-- Name: join_account_study join_account_study_study_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.join_account_study
    ADD CONSTRAINT join_account_study_study_id_fkey FOREIGN KEY (study_id) REFERENCES public.study(id) ON DELETE CASCADE;


--
-- Name: join_role_permission join_role_permission_permission_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.join_role_permission
    ADD CONSTRAINT join_role_permission_permission_id_fkey FOREIGN KEY (permission_id) REFERENCES public.permission(id) ON DELETE CASCADE;


--
-- Name: join_role_permission join_role_permission_role_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.join_role_permission
    ADD CONSTRAINT join_role_permission_role_id_fkey FOREIGN KEY (role_id) REFERENCES public.role(id) ON DELETE CASCADE;


--
-- Name: join_study_role join_study_role_role_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.join_study_role
    ADD CONSTRAINT join_study_role_role_id_fkey FOREIGN KEY (role_id) REFERENCES public.role(id) ON DELETE CASCADE;


--
-- Name: join_study_role join_study_role_study_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.join_study_role
    ADD CONSTRAINT join_study_role_study_id_fkey FOREIGN KEY (study_id) REFERENCES public.study(id);


--
-- Name: permission permission__action_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.permission
    ADD CONSTRAINT permission__action_id_fkey FOREIGN KEY (_action_id) REFERENCES public.action(id) ON DELETE CASCADE;


--
-- Name: permission permission__resource_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.permission
    ADD CONSTRAINT permission__resource_id_fkey FOREIGN KEY (_resource_id) REFERENCES public.resource(id) ON DELETE CASCADE;


--
-- PostgreSQL database dump complete
--

--
-- PostgreSQL database cluster dump complete
--

