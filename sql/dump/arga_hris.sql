--
-- PostgreSQL database dump
--

-- Dumped from database version 17.5 (Ubuntu 17.5-1.pgdg24.04+1)
-- Dumped by pg_dump version 17.5 (Ubuntu 17.5-1.pgdg24.04+1)

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET transaction_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- Name: dblink; Type: EXTENSION; Schema: -; Owner: -
--

CREATE EXTENSION IF NOT EXISTS dblink WITH SCHEMA public;


--
-- Name: EXTENSION dblink; Type: COMMENT; Schema: -; Owner: 
--

COMMENT ON EXTENSION dblink IS 'connect to other PostgreSQL databases from within a database';


SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: alembic_version; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.alembic_version (
    version_num character varying(32) NOT NULL
);


ALTER TABLE public.alembic_version OWNER TO postgres;

--
-- Name: attendances; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.attendances (
    id integer NOT NULL,
    employee_id integer NOT NULL,
    org_unit_id integer,
    attendance_date date NOT NULL,
    status character varying(50) DEFAULT 'absent'::character varying NOT NULL,
    check_in_time timestamp with time zone,
    check_out_time timestamp with time zone,
    work_hours numeric(5,2),
    created_by integer,
    check_in_submitted_at timestamp with time zone,
    check_in_submitted_ip character varying(50),
    check_in_notes text,
    check_in_selfie_path character varying(500),
    check_out_submitted_at timestamp with time zone,
    check_out_submitted_ip character varying(50),
    check_out_notes text,
    check_out_selfie_path character varying(500),
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL,
    check_in_latitude numeric(10,8),
    check_in_longitude numeric(11,8),
    check_in_location_name character varying(500),
    check_out_latitude numeric(10,8),
    check_out_longitude numeric(11,8),
    check_out_location_name character varying(500),
    overtime_hours numeric(5,2)
);


ALTER TABLE public.attendances OWNER TO postgres;

--
-- Name: COLUMN attendances.employee_id; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.attendances.employee_id IS 'Employee ID from workforce service';


--
-- Name: COLUMN attendances.org_unit_id; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.attendances.org_unit_id IS 'Org unit ID for display purposes';


--
-- Name: COLUMN attendances.work_hours; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.attendances.work_hours IS 'Calculated work hours in decimal (e.g., 8.5 for 8 hours 30 minutes)';


--
-- Name: COLUMN attendances.created_by; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.attendances.created_by IS 'User/Employee ID who created this record';


--
-- Name: COLUMN attendances.check_in_selfie_path; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.attendances.check_in_selfie_path IS 'GCP storage path for check-in selfie (mandatory when check-in)';


--
-- Name: COLUMN attendances.check_out_selfie_path; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.attendances.check_out_selfie_path IS 'GCP storage path for check-out selfie (mandatory when check-out)';


--
-- Name: COLUMN attendances.check_in_latitude; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.attendances.check_in_latitude IS 'Check-in latitude coordinate';


--
-- Name: COLUMN attendances.check_in_longitude; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.attendances.check_in_longitude IS 'Check-in longitude coordinate';


--
-- Name: COLUMN attendances.check_in_location_name; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.attendances.check_in_location_name IS 'Check-in location address from reverse geocoding';


--
-- Name: COLUMN attendances.check_out_latitude; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.attendances.check_out_latitude IS 'Check-out latitude coordinate';


--
-- Name: COLUMN attendances.check_out_longitude; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.attendances.check_out_longitude IS 'Check-out longitude coordinate';


--
-- Name: COLUMN attendances.check_out_location_name; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.attendances.check_out_location_name IS 'Check-out location address from reverse geocoding';


--
-- Name: COLUMN attendances.overtime_hours; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.attendances.overtime_hours IS 'Overtime hours after 18:00 (e.g., 2.5 for 2 hours 30 minutes)';


--
-- Name: attendances_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.attendances_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.attendances_id_seq OWNER TO postgres;

--
-- Name: attendances_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.attendances_id_seq OWNED BY public.attendances.id;


--
-- Name: guest_accounts; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.guest_accounts (
    id integer NOT NULL,
    user_id integer NOT NULL,
    guest_type character varying(50) NOT NULL,
    valid_from timestamp with time zone NOT NULL,
    valid_until timestamp with time zone NOT NULL,
    sponsor_id integer,
    notes text,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.guest_accounts OWNER TO postgres;

--
-- Name: guest_accounts_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.guest_accounts_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.guest_accounts_id_seq OWNER TO postgres;

--
-- Name: guest_accounts_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.guest_accounts_id_seq OWNED BY public.guest_accounts.id;


--
-- Name: job_executions; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.job_executions (
    id integer NOT NULL,
    job_id character varying(100) NOT NULL,
    started_at timestamp with time zone NOT NULL,
    finished_at timestamp with time zone,
    duration_seconds numeric(10,3),
    success boolean DEFAULT false NOT NULL,
    message text,
    error_trace text,
    result_data json,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone
);


ALTER TABLE public.job_executions OWNER TO postgres;

--
-- Name: COLUMN job_executions.job_id; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.job_executions.job_id IS 'Unique identifier job';


--
-- Name: COLUMN job_executions.started_at; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.job_executions.started_at IS 'Waktu mulai eksekusi';


--
-- Name: COLUMN job_executions.finished_at; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.job_executions.finished_at IS 'Waktu selesai eksekusi';


--
-- Name: COLUMN job_executions.duration_seconds; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.job_executions.duration_seconds IS 'Durasi eksekusi dalam detik';


--
-- Name: COLUMN job_executions.success; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.job_executions.success IS 'Status keberhasilan eksekusi';


--
-- Name: COLUMN job_executions.message; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.job_executions.message IS 'Pesan hasil eksekusi';


--
-- Name: COLUMN job_executions.error_trace; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.job_executions.error_trace IS 'Stack trace jika error';


--
-- Name: COLUMN job_executions.result_data; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.job_executions.result_data IS 'Data hasil eksekusi (JSON)';


--
-- Name: job_executions_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.job_executions_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.job_executions_id_seq OWNER TO postgres;

--
-- Name: job_executions_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.job_executions_id_seq OWNED BY public.job_executions.id;


--
-- Name: leave_requests; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.leave_requests (
    id integer NOT NULL,
    employee_id integer NOT NULL,
    leave_type character varying(50) NOT NULL,
    start_date date NOT NULL,
    end_date date NOT NULL,
    total_days integer NOT NULL,
    reason text NOT NULL,
    created_by integer,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL,
    CONSTRAINT check_leave_type CHECK (((leave_type)::text = ANY ((ARRAY['leave'::character varying, 'holiday'::character varying])::text[]))),
    CONSTRAINT check_total_days_positive CHECK ((total_days > 0))
);


ALTER TABLE public.leave_requests OWNER TO postgres;

--
-- Name: leave_requests_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.leave_requests_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.leave_requests_id_seq OWNER TO postgres;

--
-- Name: leave_requests_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.leave_requests_id_seq OWNED BY public.leave_requests.id;


--
-- Name: permissions; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.permissions (
    id integer NOT NULL,
    code character varying(100) NOT NULL,
    description text,
    resource character varying(50) NOT NULL,
    action character varying(50) NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.permissions OWNER TO postgres;

--
-- Name: permissions_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.permissions_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.permissions_id_seq OWNER TO postgres;

--
-- Name: permissions_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.permissions_id_seq OWNED BY public.permissions.id;


--
-- Name: role_permissions; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.role_permissions (
    role_id integer NOT NULL,
    permission_id integer NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.role_permissions OWNER TO postgres;

--
-- Name: roles; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.roles (
    id integer NOT NULL,
    name character varying(100) NOT NULL,
    description text,
    is_system boolean DEFAULT false NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.roles OWNER TO postgres;

--
-- Name: roles_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.roles_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.roles_id_seq OWNER TO postgres;

--
-- Name: roles_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.roles_id_seq OWNED BY public.roles.id;


--
-- Name: user_roles; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.user_roles (
    user_id integer NOT NULL,
    role_id integer NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.user_roles OWNER TO postgres;

--
-- Name: users; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.users (
    id integer NOT NULL,
    sso_id integer,
    employee_id integer,
    org_unit_id integer,
    email character varying(255) NOT NULL,
    first_name character varying(100) NOT NULL,
    last_name character varying(100) NOT NULL,
    account_type character varying(20) DEFAULT 'regular'::character varying NOT NULL,
    is_active boolean DEFAULT true NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL,
    employee_deleted_at timestamp with time zone
);


ALTER TABLE public.users OWNER TO postgres;

--
-- Name: users_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.users_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.users_id_seq OWNER TO postgres;

--
-- Name: users_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.users_id_seq OWNED BY public.users.id;


--
-- Name: work_submissions; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.work_submissions (
    id integer NOT NULL,
    employee_id integer NOT NULL,
    submission_month date NOT NULL,
    title character varying(255) NOT NULL,
    description text,
    files jsonb DEFAULT '[]'::jsonb NOT NULL,
    status character varying(20) DEFAULT 'draft'::character varying NOT NULL,
    submitted_at timestamp with time zone,
    created_by integer,
    created_at timestamp with time zone NOT NULL,
    updated_at timestamp with time zone NOT NULL,
    CONSTRAINT check_submission_status_valid CHECK (((status)::text = ANY ((ARRAY['draft'::character varying, 'submitted'::character varying])::text[])))
);


ALTER TABLE public.work_submissions OWNER TO postgres;

--
-- Name: COLUMN work_submissions.submission_month; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.work_submissions.submission_month IS 'Bulan submission (always 1st day of month)';


--
-- Name: COLUMN work_submissions.title; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.work_submissions.title IS 'Judul submission';


--
-- Name: COLUMN work_submissions.description; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.work_submissions.description IS 'Deskripsi detail pekerjaan';


--
-- Name: COLUMN work_submissions.files; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.work_submissions.files IS 'Array of file metadata (file_name, file_path, file_size, file_type)';


--
-- Name: COLUMN work_submissions.status; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.work_submissions.status IS 'Status: draft or submitted';


--
-- Name: COLUMN work_submissions.submitted_at; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.work_submissions.submitted_at IS 'Timestamp when status changed to submitted';


--
-- Name: COLUMN work_submissions.created_by; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.work_submissions.created_by IS 'User ID who created this submission';


--
-- Name: work_submissions_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.work_submissions_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.work_submissions_id_seq OWNER TO postgres;

--
-- Name: work_submissions_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.work_submissions_id_seq OWNED BY public.work_submissions.id;


--
-- Name: attendances id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.attendances ALTER COLUMN id SET DEFAULT nextval('public.attendances_id_seq'::regclass);


--
-- Name: guest_accounts id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.guest_accounts ALTER COLUMN id SET DEFAULT nextval('public.guest_accounts_id_seq'::regclass);


--
-- Name: job_executions id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.job_executions ALTER COLUMN id SET DEFAULT nextval('public.job_executions_id_seq'::regclass);


--
-- Name: leave_requests id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.leave_requests ALTER COLUMN id SET DEFAULT nextval('public.leave_requests_id_seq'::regclass);


--
-- Name: permissions id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.permissions ALTER COLUMN id SET DEFAULT nextval('public.permissions_id_seq'::regclass);


--
-- Name: roles id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.roles ALTER COLUMN id SET DEFAULT nextval('public.roles_id_seq'::regclass);


--
-- Name: users id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.users ALTER COLUMN id SET DEFAULT nextval('public.users_id_seq'::regclass);


--
-- Name: work_submissions id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.work_submissions ALTER COLUMN id SET DEFAULT nextval('public.work_submissions_id_seq'::regclass);


--
-- Data for Name: alembic_version; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.alembic_version (version_num) FROM stdin;
4edd379a3c40
\.


--
-- Data for Name: attendances; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.attendances (id, employee_id, org_unit_id, attendance_date, status, check_in_time, check_out_time, work_hours, created_by, check_in_submitted_at, check_in_submitted_ip, check_in_notes, check_in_selfie_path, check_out_submitted_at, check_out_submitted_ip, check_out_notes, check_out_selfie_path, created_at, updated_at, check_in_latitude, check_in_longitude, check_in_location_name, check_out_latitude, check_out_longitude, check_out_location_name, overtime_hours) FROM stdin;
4	40	11	2025-11-06	present	2025-11-06 02:15:52.457739+00	2025-11-06 09:43:31.892402+00	7.46	40	2025-11-06 02:15:52.457739+00	182.253.63.31	\N	attendances/40/check_in/2025-11-06/ca0764b9-5be6-4597-b965-47fe3a3a6d9a.jpeg	2025-11-06 09:43:31.892402+00	103.140.189.174	Lupa absen pulang	attendances/40/check_out/2025-11-06/0bd90dee-e03d-43f0-ac45-1326b4f8fb21.jpeg	2025-11-06 02:15:53.331817+00	2025-11-06 09:43:33.517024+00	-5.38763591	105.28016171	Jalan Alam Kurnia, Kalibalau Kencana, Bandar Lampung, Lampung, Sumatra, 35133, Indonesia	-5.38228033	105.25719211	Pelita, Bandar Lampung, Lampung, Sumatra, 35142, Indonesia	\N
9	41	12	2025-11-06	present	2025-11-06 02:56:32.602765+00	2025-11-06 10:10:17.667403+00	7.23	41	2025-11-06 02:56:32.602765+00	182.253.63.31	\N	attendances/41/check_in/2025-11-06/96612afe-2f67-4b00-8056-dad308fdb263.jpeg	2025-11-06 10:10:17.667403+00	182.253.63.31	\N	attendances/41/check_out/2025-11-06/aaab97a6-da4b-4f56-97f4-d3c684860822.jpeg	2025-11-06 02:56:33.477616+00	2025-11-06 10:10:18.684902+00	-5.39028740	105.27800970	Kalibalau Kencana, Bandar Lampung, Lampung, Sumatra, 35133, Indonesia	-5.38757780	105.28016650	Jalan Alam Cantik, Kalibalau Kencana, Bandar Lampung, Lampung, Sumatra, 35133, Indonesia	\N
8	44	17	2025-11-06	present	2025-11-06 02:53:30.951148+00	2025-11-06 10:27:50.145992+00	7.57	44	2025-11-06 02:53:30.951148+00	182.253.63.31	\N	attendances/44/check_in/2025-11-06/560a9666-3227-406e-80f7-4acf8004e8cb.jpeg	2025-11-06 10:27:50.145992+00	182.3.104.40	\N	attendances/44/check_out/2025-11-06/e3d96958-ef2c-413c-89a2-0d00d6c9145c.jpeg	2025-11-06 02:53:31.687945+00	2025-11-06 10:27:50.965926+00	-5.38757390	105.28016740	Jalan Alam Cantik, Kalibalau Kencana, Bandar Lampung, Lampung, Sumatra, 35133, Indonesia	-5.38757400	105.28016870	Jalan Alam Cantik, Kalibalau Kencana, Bandar Lampung, Lampung, Sumatra, 35133, Indonesia	\N
5	14	11	2025-11-06	present	2025-11-06 02:21:54.688026+00	2025-11-06 10:29:39.9514+00	8.13	14	2025-11-06 02:21:54.688026+00	182.253.63.31	\N	attendances/14/check_in/2025-11-06/bbc7eca2-331a-454f-b948-adc60631ae94.jpeg	2025-11-06 10:29:39.9514+00	182.253.63.31	\N	attendances/14/check_out/2025-11-06/3de249f2-556c-4693-a134-2622ed6430d3.jpeg	2025-11-06 02:21:55.497529+00	2025-11-06 10:29:40.695185+00	-5.39028740	105.27800970	Kalibalau Kencana, Bandar Lampung, Lampung, Sumatra, 35133, Indonesia	-5.39028740	105.27800970	Kalibalau Kencana, Bandar Lampung, Lampung, Sumatra, 35133, Indonesia	\N
888	23	33	2025-12-09	absent	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	2025-12-09 16:00:00.019778+00	2025-12-09 16:00:00.019784+00	\N	\N	\N	\N	\N	\N	\N
11	22	15	2025-11-06	absent	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	2025-11-06 16:00:00.207259+00	2025-11-06 16:00:00.207267+00	\N	\N	\N	\N	\N	\N	\N
893	50	23	2025-12-09	absent	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	2025-12-09 16:00:00.066253+00	2025-12-09 16:00:00.066258+00	\N	\N	\N	\N	\N	\N	\N
898	48	23	2025-12-09	absent	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	2025-12-09 16:00:00.093488+00	2025-12-09 16:00:00.093493+00	\N	\N	\N	\N	\N	\N	\N
903	56	27	2025-12-09	absent	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	2025-12-09 16:00:00.11461+00	2025-12-09 16:00:00.114615+00	\N	\N	\N	\N	\N	\N	\N
908	63	25	2025-12-09	absent	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	2025-12-09 16:00:00.149982+00	2025-12-09 16:00:00.149987+00	\N	\N	\N	\N	\N	\N	\N
737	22	\N	2025-12-04	invalid	2025-12-04 14:21:14.733958+00	\N	\N	22	2025-12-04 14:21:14.733958+00	103.105.82.245	\N	attendances/22/check_in/2025-12-04/0857f335-a09d-4279-bc92-e38fb205ce87.jpeg	\N	\N	\N	\N	2025-12-04 14:21:16.009758+00	2025-12-04 16:30:00.011875+00	-5.36018500	105.24746850	Sepang Jaya, Bandar Lampung, Lampung, Sumatra, 35141, Indonesia	\N	\N	\N	\N
915	23	33	2025-12-10	present	2025-12-10 02:13:11.278647+00	2025-12-10 10:35:10.025364+00	8.37	23	2025-12-10 02:13:11.278647+00	140.213.115.45	\N	attendances/23/check_in/2025-12-10/7d558e4a-5089-4280-a463-66974c32eb6c.jpeg	2025-12-10 10:35:10.025364+00	140.213.115.239	\N	attendances/23/check_out/2025-12-10/942136b9-2693-47ae-a0de-67acb535ee39.jpeg	2025-12-10 02:13:12.16721+00	2025-12-10 10:35:11.301267+00	-5.38752255	105.28018734	Jalan Alam Cantik, Kalibalau Kencana, Bandar Lampung, Lampung, Sumatra, 35133, Indonesia	-5.38755022	105.28018098	Jalan Alam Cantik, Kalibalau Kencana, Bandar Lampung, Lampung, Sumatra, 35133, Indonesia	0.00
914	42	28	2025-12-10	present	2025-12-10 02:02:54.697588+00	2025-12-10 13:22:00.965288+00	11.32	42	2025-12-10 02:02:54.697588+00	103.105.82.245	\N	attendances/42/check_in/2025-12-10/333dda29-9ca1-4689-bade-cbb0f998cc6e.jpeg	2025-12-10 13:22:00.965288+00	182.3.100.118	\N	attendances/42/check_out/2025-12-10/83ecbf3a-6ea4-4f54-9cb3-15a3bb322f41.jpeg	2025-12-10 02:02:55.685519+00	2025-12-10 13:22:01.835561+00	-5.38758480	105.28015830	Jalan Alam Kurnia, Kalibalau Kencana, Bandar Lampung, Lampung, Sumatra, 35133, Indonesia	-5.38730290	105.27308420	Way Halim Permai, Bandar Lampung, Lampung, Sumatra, 35136, Indonesia	0.00
1133	22	33	2025-12-17	present	2025-12-17 02:16:18.553564+00	2025-12-17 13:33:44.929825+00	11.29	22	2025-12-17 02:16:18.553564+00	103.105.82.243	\N	attendances/22/check_in/2025-12-17/77132ac8-f6a4-4da8-8fd1-4b9a510af34e.jpeg	2025-12-17 13:33:44.929825+00	103.105.82.243	\N	attendances/22/check_out/2025-12-17/c9c815c4-194a-4554-9335-a4f06620490b.jpeg	2025-12-17 02:16:19.638346+00	2025-12-17 13:33:46.748123+00	-5.37821410	105.26996230	Jalan Mohammad Nur 3, Perumnas Way Halim, Bandar Lampung, Lampung, Sumatra, 35132, Indonesia	-5.37821410	105.26996230	Jalan Mohammad Nur 3, Perumnas Way Halim, Bandar Lampung, Lampung, Sumatra, 35132, Indonesia	0.00
25	13	10	2025-11-06	absent	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	2025-11-06 16:00:00.443138+00	2025-11-06 16:00:00.443143+00	\N	\N	\N	\N	\N	\N	\N
30	20	14	2025-11-06	absent	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	2025-11-06 16:00:00.482264+00	2025-11-06 16:00:00.48227+00	\N	\N	\N	\N	\N	\N	\N
31	39	17	2025-11-06	hybrid	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	2025-11-06 16:00:00.487428+00	2025-11-06 16:00:00.487433+00	\N	\N	\N	\N	\N	\N	\N
32	43	17	2025-11-06	hybrid	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	2025-11-06 16:00:00.49363+00	2025-11-06 16:00:00.493634+00	\N	\N	\N	\N	\N	\N	\N
2	42	11	2025-11-06	invalid	2025-11-06 02:03:23.307078+00	\N	\N	42	2025-11-06 02:03:23.307078+00	110.137.36.86	\N	attendances/42/check_in/2025-11-06/8389eac1-cc09-4a2a-8920-6e62adc38218.jpg	\N	\N	\N	\N	2025-11-06 02:03:24.465801+00	2025-11-06 16:59:00.104753+00	-5.39676440	105.27800960	Gang M. Saleh, Tanjung Baru, Bandar Lampung, Lampung, Sumatra, 35227, Indonesia	\N	\N	\N	\N
3	23	15	2025-11-06	invalid	2025-11-06 02:09:06.838903+00	\N	\N	23	2025-11-06 02:09:06.838903+00	140.213.112.100	\N	attendances/23/check_in/2025-11-06/1a39f127-72b4-4869-99de-deba428df80e.jpeg	\N	\N	\N	\N	2025-11-06 02:09:07.701+00	2025-11-06 16:59:00.118166+00	-5.38741699	105.28005746	Jalan Alam Kurnia, Kalibalau Kencana, Bandar Lampung, Lampung, Sumatra, 35133, Indonesia	\N	\N	\N	\N
6	24	15	2025-11-06	invalid	2025-11-06 02:24:03.139798+00	\N	\N	24	2025-11-06 02:24:03.139798+00	182.253.63.31	\N	attendances/24/check_in/2025-11-06/ee665faf-f46f-404e-aa7c-f9b3329a6943.jpg	\N	\N	\N	\N	2025-11-06 02:24:04.098848+00	2025-11-06 16:59:00.119723+00	-5.38759990	105.28019740	Jalan Alam Cantik, Kalibalau Kencana, Bandar Lampung, Lampung, Sumatra, 35133, Indonesia	\N	\N	\N	\N
7	15	12	2025-11-06	invalid	2025-11-06 02:52:52.4328+00	\N	\N	15	2025-11-06 02:52:52.4328+00	114.125.233.12	\N	attendances/15/check_in/2025-11-06/d6019544-e3bb-4a0e-8496-556190b01bdc.jpeg	\N	\N	\N	\N	2025-11-06 02:52:53.185614+00	2025-11-06 16:59:00.120665+00	-5.38757410	105.28016560	Jalan Alam Cantik, Kalibalau Kencana, Bandar Lampung, Lampung, Sumatra, 35133, Indonesia	\N	\N	\N	\N
37	41	12	2025-11-07	present	2025-11-07 02:53:29.396904+00	2025-11-07 09:48:32.610096+00	6.92	41	2025-11-07 02:53:29.396904+00	182.253.63.31	\N	attendances/41/check_in/2025-11-07/6c3acdf8-6622-4ce6-b6d2-27bf0d6d0035.jpeg	2025-11-07 09:48:32.610096+00	182.253.63.30	\N	attendances/41/check_out/2025-11-07/12a720c1-e587-4601-8c6d-0292fa05b749.jpeg	2025-11-07 02:53:30.221112+00	2025-11-07 09:48:33.957142+00	-5.38757080	105.28016430	Jalan Alam Cantik, Kalibalau Kencana, Bandar Lampung, Lampung, Sumatra, 35133, Indonesia	-5.38756870	105.28014850	Jalan Alam Cantik, Kalibalau Kencana, Bandar Lampung, Lampung, Sumatra, 35133, Indonesia	\N
38	44	17	2025-11-07	present	2025-11-07 03:09:54.211717+00	2025-11-07 11:02:18.141059+00	7.87	44	2025-11-07 03:09:54.211717+00	182.253.63.31	\N	attendances/44/check_in/2025-11-07/234e2039-8e7d-475f-907a-445c303f9abf.jpeg	2025-11-07 11:02:18.141059+00	114.10.102.248	\N	attendances/44/check_out/2025-11-07/5eb781b8-3db6-4d86-8947-1f54b0efcee3.jpeg	2025-11-07 03:09:55.136255+00	2025-11-07 11:02:19.175202+00	-5.38757470	105.28016900	Jalan Alam Cantik, Kalibalau Kencana, Bandar Lampung, Lampung, Sumatra, 35133, Indonesia	-5.38757550	105.28017050	Jalan Alam Cantik, Kalibalau Kencana, Bandar Lampung, Lampung, Sumatra, 35133, Indonesia	\N
35	14	11	2025-11-07	present	2025-11-07 02:21:48.202193+00	2025-11-07 11:02:28.023509+00	8.68	14	2025-11-07 02:21:48.202193+00	182.253.63.31	\N	attendances/14/check_in/2025-11-07/8ec950a6-53c0-475c-94b9-60d900246a94.jpeg	2025-11-07 11:02:28.023509+00	182.3.103.235	\N	attendances/14/check_out/2025-11-07/9414c1d0-6eec-4631-ba14-24b72bcc5c79.jpeg	2025-11-07 02:21:48.931844+00	2025-11-07 11:02:28.751501+00	-5.39211620	105.28239930	Gang Panorama 1, Kalibalau Kencana, Bandar Lampung, Lampung, Sumatra, 35133, Indonesia	-5.38757450	105.28016620	Jalan Alam Cantik, Kalibalau Kencana, Bandar Lampung, Lampung, Sumatra, 35133, Indonesia	\N
61	39	17	2025-11-07	hybrid	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	2025-11-07 16:00:00.820289+00	2025-11-07 16:00:00.820293+00	\N	\N	\N	\N	\N	\N	\N
36	42	11	2025-11-07	present	2025-11-07 02:37:20.172856+00	2025-11-07 10:02:14.463774+00	7.42	42	2025-11-07 02:37:20.172856+00	182.253.63.31	\N	attendances/42/check_in/2025-11-07/b6e2f747-cea0-49d8-b075-8556c9960e03.jpeg	2025-11-07 10:02:14.463774+00	182.253.63.30	\N	attendances/42/check_out/2025-11-07/37cbb133-7244-4eee-aed7-7a3d253eba1a.jpeg	2025-11-07 02:37:20.998019+00	2025-11-07 10:02:15.261861+00	-5.39211620	105.28239930	Gang Panorama 1, Kalibalau Kencana, Bandar Lampung, Lampung, Sumatra, 35133, Indonesia	-5.38757600	105.28016980	Jalan Alam Cantik, Kalibalau Kencana, Bandar Lampung, Lampung, Sumatra, 35133, Indonesia	\N
42	23	15	2025-11-07	present	2025-11-07 10:19:04.904841+00	2025-11-07 10:19:16.80348+00	0.00	23	2025-11-07 10:19:04.904841+00	112.78.141.78	\N	attendances/23/check_in/2025-11-07/e2868e56-b3fc-43cd-a463-ade236388519.jpeg	2025-11-07 10:19:16.80348+00	112.78.141.78	\N	attendances/23/check_out/2025-11-07/790fff72-11d8-41e9-8bbd-b397e4256f26.jpeg	2025-11-07 10:19:05.853162+00	2025-11-07 10:19:17.513464+00	-6.14033039	106.88190555	Homefresh - Sunter Jaya, Jalan Danau Sunter Utara, Sunter Jaya, Tanjung Priok, Jakarta Utara, Daerah Khusus Ibukota Jakarta, Jawa, 14350, Indonesia	-6.14033039	106.88190555	Homefresh - Sunter Jaya, Jalan Danau Sunter Utara, Sunter Jaya, Tanjung Priok, Jakarta Utara, Daerah Khusus Ibukota Jakarta, Jawa, 14350, Indonesia	\N
34	40	11	2025-11-07	present	2025-11-07 02:19:59.0441+00	2025-11-07 10:46:08.030735+00	8.44	40	2025-11-07 02:19:59.0441+00	182.253.63.31	\N	attendances/40/check_in/2025-11-07/859b5fa0-fa31-4f76-b3a4-aef985dce967.jpeg	2025-11-07 10:46:08.030735+00	182.253.63.30	\N	attendances/40/check_out/2025-11-07/eefa8b06-8c47-4e55-8f9e-964bb19e8cea.jpeg	2025-11-07 02:19:59.843891+00	2025-11-07 10:46:08.876257+00	-5.38759985	105.28017772	Jalan Alam Cantik, Kalibalau Kencana, Bandar Lampung, Lampung, Sumatra, 35133, Indonesia	-5.38756628	105.28018580	Jalan Alam Cantik, Kalibalau Kencana, Bandar Lampung, Lampung, Sumatra, 35133, Indonesia	\N
738	13	20	2025-12-04	present	\N	\N	\N	1	\N	\N	\N	\N	\N	\N	\N	\N	2025-12-04 15:03:57.86807+00	2025-12-04 15:03:57.868074+00	\N	\N	\N	\N	\N	\N	\N
889	45	21	2025-12-09	absent	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	2025-12-09 16:00:00.036292+00	2025-12-09 16:00:00.036297+00	\N	\N	\N	\N	\N	\N	\N
894	51	23	2025-12-09	absent	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	2025-12-09 16:00:00.072186+00	2025-12-09 16:00:00.072192+00	\N	\N	\N	\N	\N	\N	\N
899	52	24	2025-12-09	absent	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	2025-12-09 16:00:00.098505+00	2025-12-09 16:00:00.098509+00	\N	\N	\N	\N	\N	\N	\N
904	60	29	2025-12-09	absent	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	2025-12-09 16:00:00.120682+00	2025-12-09 16:00:00.120687+00	\N	\N	\N	\N	\N	\N	\N
909	43	32	2025-12-09	hybrid	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	2025-12-09 16:00:00.156186+00	2025-12-09 16:00:00.156191+00	\N	\N	\N	\N	\N	\N	\N
910	15	21	2025-12-10	invalid	2025-12-10 01:32:58.719091+00	\N	\N	15	2025-12-10 01:32:58.719091+00	182.3.104.18	\N	attendances/15/check_in/2025-12-10/6b759641-ef43-4211-8587-18a16be1fefa.jpeg	\N	\N	\N	\N	2025-12-10 01:33:00.394384+00	2025-12-10 16:30:00.043635+00	-5.38757010	105.28017500	Jalan Alam Cantik, Kalibalau Kencana, Bandar Lampung, Lampung, Sumatra, 35133, Indonesia	\N	\N	\N	\N
55	13	10	2025-11-07	absent	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	2025-11-07 16:00:00.775071+00	2025-11-07 16:00:00.775076+00	\N	\N	\N	\N	\N	\N	\N
1144	39	32	2025-12-17	present	2025-12-17 04:40:40.512185+00	2025-12-17 08:44:23.48205+00	4.06	39	2025-12-17 04:40:40.512185+00	103.105.82.243	\N	attendances/39/check_in/2025-12-17/347d77fe-b927-434a-887a-a6791cd44056.jpeg	2025-12-17 08:44:23.48205+00	103.105.82.243	\N	attendances/39/check_out/2025-12-17/5ceadb84-a34e-4aa3-958c-1e5919a70900.jpeg	2025-12-17 04:40:41.437262+00	2025-12-17 08:44:25.076506+00	-5.38758280	105.28015540	Jalan Alam Kurnia, Kalibalau Kencana, Bandar Lampung, Lampung, Sumatra, 35133, Indonesia	-5.38758500	105.28015900	Jalan Alam Kurnia, Kalibalau Kencana, Bandar Lampung, Lampung, Sumatra, 35133, Indonesia	0.00
1138	41	21	2025-12-17	present	2025-12-17 02:45:14.393294+00	2025-12-17 10:34:03.309133+00	7.81	41	2025-12-17 02:45:14.393294+00	103.105.82.243	\N	attendances/41/check_in/2025-12-17/9c4b98d4-5042-43bf-8270-a52f31684772.jpeg	2025-12-17 10:34:03.309133+00	114.10.100.189	\N	attendances/41/check_out/2025-12-17/64309df5-d9be-4d57-804c-4854557344a3.jpeg	2025-12-17 02:45:15.152609+00	2025-12-17 10:34:04.348277+00	-5.38757354	105.28018932	Jalan Alam Cantik, Kalibalau Kencana, Bandar Lampung, Lampung, Sumatra, 35133, Indonesia	-5.38757069	105.28016373	Jalan Alam Cantik, Kalibalau Kencana, Bandar Lampung, Lampung, Sumatra, 35133, Indonesia	0.00
1135	64	24	2025-12-17	present	2025-12-17 02:23:58.273222+00	2025-12-17 13:53:55.180835+00	11.50	64	2025-12-17 02:23:58.273222+00	110.137.39.211	hp bermasalah 	attendances/64/check_in/2025-12-17/398cb816-82b4-427a-bc0d-0d1c9bced998.jpeg	2025-12-17 13:53:55.180835+00	110.137.39.211	\N	attendances/64/check_out/2025-12-17/4d5fa55d-41b0-4616-be9c-5e872feb45f8.jpeg	2025-12-17 02:23:58.989258+00	2025-12-17 13:53:55.931708+00	-4.85927062	104.93110968	Tanjung Harapan, Lampung Utara, Lampung, Sumatra, 34511, Indonesia	-4.85921878	104.93109159	Tanjung Harapan, Lampung Utara, Lampung, Sumatra, 34511, Indonesia	0.00
62	43	17	2025-11-07	hybrid	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	2025-11-07 16:00:00.828054+00	2025-11-07 16:00:00.828059+00	\N	\N	\N	\N	\N	\N	\N
67	41	12	2025-11-08	present	2025-11-08 02:34:02.208833+00	2025-11-08 07:21:37.881275+00	4.79	41	2025-11-08 02:34:02.208833+00	182.253.63.30	\N	attendances/41/check_in/2025-11-08/e57235cf-c75b-460c-b5a8-061206098f65.jpeg	2025-11-08 07:21:37.881275+00	182.253.63.30	\N	attendances/41/check_out/2025-11-08/2c7f05dc-87e0-42ae-831b-da4a8513a199.jpeg	2025-11-08 02:34:02.916303+00	2025-11-08 07:21:39.165876+00	-5.38756960	105.28016940	Jalan Alam Cantik, Kalibalau Kencana, Bandar Lampung, Lampung, Sumatra, 35133, Indonesia	-5.38757660	105.28016940	Jalan Alam Cantik, Kalibalau Kencana, Bandar Lampung, Lampung, Sumatra, 35133, Indonesia	\N
66	15	12	2025-11-08	present	2025-11-08 02:30:54.399942+00	2025-11-08 07:50:14.647241+00	5.32	15	2025-11-08 02:30:54.399942+00	182.3.102.108	\N	attendances/15/check_in/2025-11-08/dbcd59b3-cb25-4bc4-852c-86296b28bdfb.jpeg	2025-11-08 07:50:14.647241+00	182.253.63.30	\N	attendances/15/check_out/2025-11-08/caa9833c-bb1c-4870-bfbb-bc0f4303ae21.jpeg	2025-11-08 02:30:55.441966+00	2025-11-08 07:50:15.520181+00	-5.38757400	105.28016850	Jalan Alam Cantik, Kalibalau Kencana, Bandar Lampung, Lampung, Sumatra, 35133, Indonesia	-5.38757350	105.28016560	Jalan Alam Cantik, Kalibalau Kencana, Bandar Lampung, Lampung, Sumatra, 35133, Indonesia	\N
65	42	11	2025-11-08	present	2025-11-08 02:25:50.127874+00	2025-11-08 07:53:38.693283+00	5.46	42	2025-11-08 02:25:50.127874+00	182.3.103.14	\N	attendances/42/check_in/2025-11-08/f5169946-e61a-4ad0-8508-1a3509253873.jpeg	2025-11-08 07:53:38.693283+00	182.253.63.30	\N	attendances/42/check_out/2025-11-08/9274e6fa-f0db-4799-9484-ca7aacd0b677.jpeg	2025-11-08 02:25:51.007318+00	2025-11-08 07:53:39.599373+00	-5.38755820	105.28017050	Jalan Alam Cantik, Kalibalau Kencana, Bandar Lampung, Lampung, Sumatra, 35133, Indonesia	-5.38757550	105.28016160	Jalan Alam Cantik, Kalibalau Kencana, Bandar Lampung, Lampung, Sumatra, 35133, Indonesia	\N
69	24	15	2025-11-08	present	2025-11-08 02:41:57.296314+00	2025-11-08 07:59:04.153332+00	5.29	24	2025-11-08 02:41:57.296314+00	182.253.63.30	\N	attendances/24/check_in/2025-11-08/3f9c1e0f-2b21-42b0-9db3-4818b6be49d2.jpeg	2025-11-08 07:59:04.153332+00	182.253.63.30	\N	attendances/24/check_out/2025-11-08/315af321-4df2-4e7a-a779-ca70f7785ce0.jpeg	2025-11-08 02:41:58.023988+00	2025-11-08 07:59:04.912144+00	-5.37816740	105.27800970	Stadion Way Halim, Harapan Jaya, Bandar Lampung, Lampung, Sumatra, 35133, Indonesia	-5.38756230	105.28014470	Jalan Alam Cantik, Kalibalau Kencana, Bandar Lampung, Lampung, Sumatra, 35133, Indonesia	\N
84	13	10	2025-11-08	absent	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	2025-11-08 16:00:03.613188+00	2025-11-08 16:00:03.613194+00	\N	\N	\N	\N	\N	\N	\N
90	39	17	2025-11-08	hybrid	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	2025-11-08 16:00:03.839673+00	2025-11-08 16:00:03.839678+00	\N	\N	\N	\N	\N	\N	\N
91	43	17	2025-11-08	hybrid	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	2025-11-08 16:00:03.904962+00	2025-11-08 16:00:03.904967+00	\N	\N	\N	\N	\N	\N	\N
63	23	15	2025-11-08	invalid	2025-11-08 01:57:28.197101+00	\N	\N	23	2025-11-08 01:57:28.197101+00	182.3.42.136	\N	attendances/23/check_in/2025-11-08/13c2d73e-5330-4684-9dcd-436c16e1b459.jpeg	\N	\N	\N	\N	2025-11-08 01:57:29.631489+00	2025-11-08 16:59:00.051671+00	-6.20918450	106.82817821	Jalan Setiabudi Timur 2, RW 01, Setiabudi, Jakarta Selatan, Daerah Khusus Ibukota Jakarta, Jawa, 12910, Indonesia	\N	\N	\N	\N
64	40	11	2025-11-08	invalid	2025-11-08 02:02:08.080846+00	\N	\N	40	2025-11-08 02:02:08.080846+00	182.253.63.37	\N	attendances/40/check_in/2025-11-08/b2c36769-505b-482b-8214-4d4c655da66e.jpeg	\N	\N	\N	\N	2025-11-08 02:02:09.110901+00	2025-11-08 16:59:00.056682+00	-5.37938874	105.24536994	Jalan Bugenvil, Segala Mider, Bandar Lampung, Lampung, Sumatra, 35148, Indonesia	\N	\N	\N	\N
70	22	15	2025-11-08	invalid	2025-11-08 03:32:41.560088+00	\N	\N	22	2025-11-08 03:32:41.560088+00	182.253.63.30	\N	attendances/22/check_in/2025-11-08/38e64604-194a-4966-a5da-45628c31dd07.jpeg	\N	\N	\N	\N	2025-11-08 03:32:42.409033+00	2025-11-08 16:59:00.057564+00	-5.39211620	105.28239930	Gang Panorama 1, Kalibalau Kencana, Bandar Lampung, Lampung, Sumatra, 35133, Indonesia	\N	\N	\N	\N
33	15	12	2025-11-07	invalid	2025-11-07 02:06:24.433683+00	\N	\N	15	2025-11-07 02:06:24.433683+00	182.3.104.114	\N	attendances/15/check_in/2025-11-07/184a27f1-d402-4147-9324-9dea606a920a.jpeg	\N	\N	\N	\N	2025-11-07 02:06:26.060565+00	2025-11-07 16:59:00.059942+00	-5.38754000	105.28014360	Jalan Alam Cantik, Kalibalau Kencana, Bandar Lampung, Lampung, Sumatra, 35133, Indonesia	\N	\N	\N	\N
39	22	15	2025-11-07	invalid	2025-11-07 03:12:37.900424+00	\N	\N	22	2025-11-07 03:12:37.900424+00	182.253.63.31	\N	attendances/22/check_in/2025-11-07/cfa7460e-a4a1-4bbb-ac0e-cc7d2075d93c.jpeg	\N	\N	\N	\N	2025-11-07 03:12:38.717148+00	2025-11-07 16:59:00.067709+00	-5.39211620	105.28239930	Gang Panorama 1, Kalibalau Kencana, Bandar Lampung, Lampung, Sumatra, 35133, Indonesia	\N	\N	\N	\N
40	20	14	2025-11-07	invalid	2025-11-07 03:36:38.79333+00	\N	\N	20	2025-11-07 03:36:38.79333+00	182.253.63.31	\N	attendances/20/check_in/2025-11-07/5c764baa-79b7-462a-a041-d7e4bf7fe065.jpeg	\N	\N	\N	\N	2025-11-07 03:36:39.619918+00	2025-11-07 16:59:00.069159+00	-5.39211620	105.28239930	Gang Panorama 1, Kalibalau Kencana, Bandar Lampung, Lampung, Sumatra, 35133, Indonesia	\N	\N	\N	\N
41	24	15	2025-11-07	invalid	2025-11-07 09:49:46.398839+00	\N	\N	24	2025-11-07 09:49:46.398839+00	114.10.100.212	\N	attendances/24/check_in/2025-11-07/57c7c2c1-f504-4664-a222-b7de812ba124.jpg	\N	\N	\N	\N	2025-11-07 09:49:47.302694+00	2025-11-07 16:59:00.069946+00	-5.38756870	105.28014600	Jalan Alam Cantik, Kalibalau Kencana, Bandar Lampung, Lampung, Sumatra, 35133, Indonesia	\N	\N	\N	\N
68	20	14	2025-11-08	present	2025-11-08 02:41:40.616078+00	2025-11-08 08:55:34.52412+00	6.23	20	2025-11-08 02:41:40.616078+00	182.253.63.30	\N	attendances/20/check_in/2025-11-08/06cfeaa9-4465-4aa1-a128-852498304cf8.jpeg	2025-11-08 08:55:34.52412+00	114.10.101.167	\N	attendances/20/check_out/2025-11-08/5490de79-129a-411a-b96d-b781b3e035a9.jpeg	2025-11-08 02:41:41.38867+00	2025-11-08 08:55:35.461259+00	-5.37816740	105.27800970	Stadion Way Halim, Harapan Jaya, Bandar Lampung, Lampung, Sumatra, 35133, Indonesia	-5.39361280	105.25736960	Kedaton, Bandar Lampung, Lampung, Sumatra, 35123, Indonesia	\N
890	46	21	2025-12-09	absent	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	2025-12-09 16:00:00.044225+00	2025-12-09 16:00:00.044229+00	\N	\N	\N	\N	\N	\N	\N
895	53	25	2025-12-09	absent	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	2025-12-09 16:00:00.077984+00	2025-12-09 16:00:00.077991+00	\N	\N	\N	\N	\N	\N	\N
747	62	30	2025-12-04	present	\N	\N	\N	1	\N	\N	\N	\N	\N	\N	\N	\N	2025-12-04 15:03:57.920053+00	2025-12-04 15:03:57.920056+00	\N	\N	\N	\N	\N	\N	\N
900	55	27	2025-12-09	absent	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	2025-12-09 16:00:00.102293+00	2025-12-09 16:00:00.102297+00	\N	\N	\N	\N	\N	\N	\N
905	61	29	2025-12-09	absent	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	2025-12-09 16:00:00.12686+00	2025-12-09 16:00:00.126866+00	\N	\N	\N	\N	\N	\N	\N
92	44	17	2025-11-08	absent	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	2025-11-08 16:00:04.054313+00	2025-11-08 16:00:04.05432+00	\N	\N	\N	\N	\N	\N	\N
71	14	11	2025-11-08	invalid	2025-11-08 03:58:00.463505+00	\N	\N	14	2025-11-08 03:58:00.463505+00	182.253.63.30	\N	attendances/14/check_in/2025-11-08/f16fc2b0-02a3-4d7e-8b92-8a4ba0841c10.jpeg	\N	\N	\N	\N	2025-11-08 03:58:01.3269+00	2025-11-08 16:59:00.058274+00	-5.39211620	105.28239930	Gang Panorama 1, Kalibalau Kencana, Bandar Lampung, Lampung, Sumatra, 35133, Indonesia	\N	\N	\N	\N
96	40	11	2025-11-10	present	2025-11-10 02:25:01.711137+00	2025-11-10 10:05:28.91101+00	7.67	40	2025-11-10 02:25:01.711137+00	182.253.63.30	\N	attendances/40/check_in/2025-11-10/d905e22a-58c0-4d74-9dd8-868f7e4f0755.jpeg	2025-11-10 10:05:28.91101+00	182.253.63.30	\N	attendances/40/check_out/2025-11-10/829985da-b0e9-4f3c-81d2-46983c3cc486.jpeg	2025-11-10 02:25:02.9375+00	2025-11-10 10:05:30.919127+00	-5.38758048	105.28016823	Jalan Alam Cantik, Kalibalau Kencana, Bandar Lampung, Lampung, Sumatra, 35133, Indonesia	-5.38760228	105.28015546	Jalan Alam Kurnia, Kalibalau Kencana, Bandar Lampung, Lampung, Sumatra, 35133, Indonesia	\N
95	42	11	2025-11-10	present	2025-11-10 02:14:13.036497+00	2025-11-10 10:07:42.66001+00	7.89	42	2025-11-10 02:14:13.036497+00	182.253.63.30	\N	attendances/42/check_in/2025-11-10/0da29be2-0f96-4b44-a565-bf4a31dc3fdd.jpeg	2025-11-10 10:07:42.66001+00	182.253.63.30	\N	attendances/42/check_out/2025-11-10/3a3dd0b0-e766-4cd3-aaf3-87098f0e0f8e.jpeg	2025-11-10 02:14:13.88161+00	2025-11-10 10:07:43.660518+00	-5.38757440	105.28016900	Jalan Alam Cantik, Kalibalau Kencana, Bandar Lampung, Lampung, Sumatra, 35133, Indonesia	-5.38757430	105.28016900	Jalan Alam Cantik, Kalibalau Kencana, Bandar Lampung, Lampung, Sumatra, 35133, Indonesia	\N
101	14	11	2025-11-10	present	2025-11-10 03:20:46.021653+00	2025-11-10 10:08:53.820262+00	6.80	14	2025-11-10 03:20:46.021653+00	182.253.63.30	\N	attendances/14/check_in/2025-11-10/e5dc59b8-1ee4-4c8c-aa17-8226cc71a1b3.jpeg	2025-11-10 10:08:53.820262+00	182.253.63.30	\N	attendances/14/check_out/2025-11-10/b59cb7a9-4104-4cd6-8812-20ca15a5c4bd.jpeg	2025-11-10 03:20:46.792735+00	2025-11-10 10:08:54.683835+00	-5.39676440	105.27800960	Gang M. Saleh, Tanjung Baru, Bandar Lampung, Lampung, Sumatra, 35227, Indonesia	-5.36358130	105.28166770	Way Dadi, Bandar Lampung, Lampung, Sumatra, 35139, Indonesia	\N
100	41	12	2025-11-10	present	2025-11-10 03:00:53.499131+00	2025-11-10 10:13:41.440851+00	7.21	41	2025-11-10 03:00:53.499131+00	182.253.63.30	\N	attendances/41/check_in/2025-11-10/b8f373ed-4ff0-4938-9265-47bc7e78d5ad.jpeg	2025-11-10 10:13:41.440851+00	182.253.63.30	\N	attendances/41/check_out/2025-11-10/e5049a92-3c6b-4454-bcf8-7c759faa44eb.jpeg	2025-11-10 03:00:54.389864+00	2025-11-10 10:13:42.526894+00	-5.38754470	105.28011950	Jalan Alam Kurnia, Kalibalau Kencana, Bandar Lampung, Lampung, Sumatra, 35133, Indonesia	-5.38757490	105.28016940	Jalan Alam Cantik, Kalibalau Kencana, Bandar Lampung, Lampung, Sumatra, 35133, Indonesia	\N
94	15	12	2025-11-10	present	2025-11-10 02:02:48.693557+00	2025-11-10 10:26:43.294175+00	8.40	15	2025-11-10 02:02:48.693557+00	182.3.100.166	\N	attendances/15/check_in/2025-11-10/1a4790b9-ab22-4dc1-a4b5-ef7fb0558569.jpeg	2025-11-10 10:26:43.294175+00	182.3.100.186	\N	attendances/15/check_out/2025-11-10/c385e3ba-70eb-4bdd-9208-fa80c792c3b3.jpeg	2025-11-10 02:02:50.043932+00	2025-11-10 10:26:44.423069+00	-5.38756000	105.28018280	Jalan Alam Cantik, Kalibalau Kencana, Bandar Lampung, Lampung, Sumatra, 35133, Indonesia	-5.38756000	105.28018280	Jalan Alam Cantik, Kalibalau Kencana, Bandar Lampung, Lampung, Sumatra, 35133, Indonesia	\N
97	20	14	2025-11-10	present	2025-11-10 02:35:39.272098+00	2025-11-10 10:47:28.155715+00	8.20	20	2025-11-10 02:35:39.272098+00	182.253.63.30	senin masuk	attendances/20/check_in/2025-11-10/97184b2c-fdc6-4be5-9665-a3c92dbafc3e.jpeg	2025-11-10 10:47:28.155715+00	182.253.63.30	\N	attendances/20/check_out/2025-11-10/49daacc0-190b-4d72-9faa-70abd5e51cb5.jpg	2025-11-10 02:35:40.070018+00	2025-11-10 10:47:29.461846+00	-5.39676440	105.27800960	Gang M. Saleh, Tanjung Baru, Bandar Lampung, Lampung, Sumatra, 35227, Indonesia	-5.36358130	105.28166770	Way Dadi, Bandar Lampung, Lampung, Sumatra, 35139, Indonesia	\N
93	23	15	2025-11-10	present	2025-11-09 22:23:59.495101+00	2025-11-10 10:48:00.240427+00	12.40	23	2025-11-09 22:23:59.495101+00	182.253.63.30	\N	attendances/23/check_in/2025-11-10/3d862d92-8a01-4103-b033-187e8755d92f.jpeg	2025-11-10 10:48:00.240427+00	140.213.116.191	\N	attendances/23/check_out/2025-11-10/ec18a941-5942-4213-b9a8-cfb85e70c1c5.jpeg	2025-11-09 22:24:01.09735+00	2025-11-10 10:48:01.12143+00	-5.38754536	105.28017912	Jalan Alam Cantik, Kalibalau Kencana, Bandar Lampung, Lampung, Sumatra, 35133, Indonesia	-5.38753157	105.28016463	Jalan Alam Cantik, Kalibalau Kencana, Bandar Lampung, Lampung, Sumatra, 35133, Indonesia	\N
99	24	15	2025-11-10	present	2025-11-10 02:51:12.954864+00	2025-11-10 10:48:01.338264+00	7.95	24	2025-11-10 02:51:12.954864+00	182.253.63.30	\N	attendances/24/check_in/2025-11-10/6ab5d676-47bb-4392-9514-4b3b27bc84d8.jpeg	2025-11-10 10:48:01.338264+00	114.10.102.48	\N	attendances/24/check_out/2025-11-10/cdab7e2e-64f2-4ec7-b221-4f57533d778f.jpeg	2025-11-10 02:51:13.961765+00	2025-11-10 10:48:02.245935+00	-5.39676440	105.27800960	Gang M. Saleh, Tanjung Baru, Bandar Lampung, Lampung, Sumatra, 35227, Indonesia	-5.38756970	105.28014890	Jalan Alam Cantik, Kalibalau Kencana, Bandar Lampung, Lampung, Sumatra, 35133, Indonesia	\N
98	22	15	2025-11-10	present	2025-11-10 02:37:43.585098+00	2025-11-10 10:48:02.851159+00	8.17	22	2025-11-10 02:37:43.585098+00	182.253.63.30	\N	attendances/22/check_in/2025-11-10/4fb33aab-7fcd-478d-a310-8da17347b5fe.jpeg	2025-11-10 10:48:02.851159+00	182.253.63.30	\N	attendances/22/check_out/2025-11-10/486d3eab-ad7b-4b2e-a71f-7582dc984201.jpeg	2025-11-10 02:37:44.279271+00	2025-11-10 10:48:03.865801+00	-5.39211620	105.28239930	Gang Panorama 1, Kalibalau Kencana, Bandar Lampung, Lampung, Sumatra, 35133, Indonesia	-5.36358130	105.28166770	Way Dadi, Bandar Lampung, Lampung, Sumatra, 35139, Indonesia	\N
760	20	31	2025-12-05	invalid	2025-12-04 22:15:13.651314+00	\N	\N	20	2025-12-04 22:15:13.651314+00	140.213.190.201	\N	attendances/20/check_in/2025-12-05/cb0277cb-f826-40d5-a607-2777cc58c662.jpeg	\N	\N	\N	\N	2025-12-04 22:15:15.265487+00	2025-12-05 16:30:00.049907+00	-5.38377302	105.28154051	Kalibalau Kencana, Bandar Lampung, Lampung, Sumatra, 35133, Indonesia	\N	\N	\N	\N
891	59	29	2025-12-09	absent	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	2025-12-09 16:00:00.051655+00	2025-12-09 16:00:00.05166+00	\N	\N	\N	\N	\N	\N	\N
896	54	25	2025-12-09	absent	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	2025-12-09 16:00:00.082517+00	2025-12-09 16:00:00.082522+00	\N	\N	\N	\N	\N	\N	\N
901	57	27	2025-12-09	absent	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	2025-12-09 16:00:00.10573+00	2025-12-09 16:00:00.105733+00	\N	\N	\N	\N	\N	\N	\N
906	47	22	2025-12-09	absent	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	2025-12-09 16:00:00.132523+00	2025-12-09 16:00:00.132528+00	\N	\N	\N	\N	\N	\N	\N
144	13	10	2025-11-11	absent	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	2025-11-11 16:00:01.119766+00	2025-11-11 16:00:01.119771+00	\N	\N	\N	\N	\N	\N	\N
150	20	14	2025-11-11	absent	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	2025-11-11 16:00:01.247161+00	2025-11-11 16:00:01.247167+00	\N	\N	\N	\N	\N	\N	\N
131	14	11	2025-11-11	invalid	2025-11-11 06:15:09.407737+00	\N	\N	14	2025-11-11 06:15:09.407737+00	103.59.44.25	\N	attendances/14/check_in/2025-11-11/31f2932c-79bb-491e-8123-f96311ba95d1.jpeg	\N	\N	\N	\N	2025-11-11 06:15:10.43188+00	2025-11-11 16:59:00.06719+00	-5.43060710	104.73919130	Gisting Bawah, Tanggamus, Lampung, Sumatra, Indonesia	\N	\N	\N	\N
757	43	32	2025-12-04	present	\N	\N	\N	1	\N	\N	\N	\N	\N	\N	\N	\N	2025-12-04 15:03:57.981667+00	2025-12-04 15:03:57.981669+00	\N	\N	\N	\N	\N	\N	\N
1140	47	22	2025-12-17	present	2025-12-17 02:45:55.706899+00	2025-12-17 10:55:40.585883+00	8.16	47	2025-12-17 02:45:55.706899+00	182.3.68.164	\N	attendances/47/check_in/2025-12-17/692fb602-b513-4bd9-8571-8f0ee3732f42.jpeg	2025-12-17 10:55:40.585883+00	182.3.104.136	\N	attendances/47/check_out/2025-12-17/a1824ec1-a6ed-4481-946d-347baf3bea74.jpeg	2025-12-17 02:45:56.395964+00	2025-12-17 10:55:41.55258+00	-5.48121900	104.92582070	Pardasuka, Pringsewu, Lampung, Sumatra, Indonesia	-5.35858490	105.06163200	Tegalsari, Pringsewu, Lampung, Sumatra, 35367, Indonesia	0.00
114	13	10	2025-11-10	absent	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	2025-11-10 16:00:00.799997+00	2025-11-10 16:00:00.800001+00	\N	\N	\N	\N	\N	\N	\N
120	39	17	2025-11-10	hybrid	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	2025-11-10 16:00:00.853199+00	2025-11-10 16:00:00.853203+00	\N	\N	\N	\N	\N	\N	\N
127	23	15	2025-11-11	present	2025-11-11 02:19:12.770992+00	2025-11-11 10:16:26.423665+00	7.95	23	2025-11-11 02:19:12.770992+00	182.253.63.30	\N	attendances/23/check_in/2025-11-11/1db1a015-179b-43fd-aa94-db93b1b1ab07.jpeg	2025-11-11 10:16:26.423665+00	182.253.63.30	\N	attendances/23/check_out/2025-11-11/807dfceb-b3b4-47a9-ae36-8ca9df5ed9e7.jpeg	2025-11-11 02:19:13.914128+00	2025-11-11 10:16:27.665078+00	-5.38753521	105.28017974	Jalan Alam Cantik, Kalibalau Kencana, Bandar Lampung, Lampung, Sumatra, 35133, Indonesia	-5.38751111	105.28019317	Jalan Alam Cantik, Kalibalau Kencana, Bandar Lampung, Lampung, Sumatra, 35133, Indonesia	\N
130	44	17	2025-11-11	present	2025-11-11 05:41:07.631641+00	2025-11-11 10:20:24.26597+00	4.65	44	2025-11-11 05:41:07.631641+00	182.253.63.30	\N	attendances/44/check_in/2025-11-11/294b3083-eba9-4f67-a47f-1fb1e3e5aaee.jpeg	2025-11-11 10:20:24.26597+00	182.253.63.30	\N	attendances/44/check_out/2025-11-11/013126c1-dbe8-4b21-96bf-70b77e8ecb99.jpeg	2025-11-11 05:41:09.125352+00	2025-11-11 10:20:24.988478+00	-5.38758130	105.28016330	Jalan Alam Cantik, Kalibalau Kencana, Bandar Lampung, Lampung, Sumatra, 35133, Indonesia	-5.38758110	105.28016420	Jalan Alam Cantik, Kalibalau Kencana, Bandar Lampung, Lampung, Sumatra, 35133, Indonesia	\N
129	22	15	2025-11-11	present	2025-11-11 02:47:40.094432+00	2025-11-11 11:22:49.660271+00	8.59	22	2025-11-11 02:47:40.094432+00	182.253.63.30	\N	attendances/22/check_in/2025-11-11/acb702ac-832f-4c0a-ab84-0d2d243bbd7d.jpeg	2025-11-11 11:22:49.660271+00	182.253.63.28	\N	attendances/22/check_out/2025-11-11/a8aabb89-bcef-43d3-9954-6d59abcd82f2.jpeg	2025-11-11 02:47:41.323306+00	2025-11-11 11:22:50.861424+00	-5.39211620	105.28239930	Gang Panorama 1, Kalibalau Kencana, Bandar Lampung, Lampung, Sumatra, 35133, Indonesia	-5.40709370	105.27557650	Unsilent Cafe, Jalan Pangeran Antasari, Tanjung Agung, Bandar Lampung, Lampung, Sumatra, 35227, Indonesia	\N
761	23	33	2025-12-05	present	2025-12-04 23:31:09.458338+00	2025-12-05 11:41:47.673297+00	12.18	23	2025-12-04 23:31:09.458338+00	103.105.82.245	\N	attendances/23/check_in/2025-12-05/6cd2478d-ccd1-4eb7-a63c-63d83206571f.jpeg	2025-12-05 11:41:47.673297+00	140.213.114.146	\N	attendances/23/check_out/2025-12-05/1413b288-9ae2-4e1e-bf74-782514e6cb61.jpeg	2025-12-04 23:31:11.103495+00	2025-12-05 11:41:49.482149+00	-5.38756075	105.28015038	Jalan Alam Cantik, Kalibalau Kencana, Bandar Lampung, Lampung, Sumatra, 35133, Indonesia	-5.68568713	105.22755831	Pulau Pahawang, Pesawaran, Lampung, Sumatra, Indonesia	0.00
764	40	28	2025-12-05	present	2025-12-05 00:06:47.169184+00	2025-12-05 15:02:40.508766+00	14.93	40	2025-12-05 00:06:47.169184+00	103.105.82.245	\N	attendances/40/check_in/2025-12-05/df0f7314-ce97-44b3-b9db-753737ae5535.jpeg	2025-12-05 15:02:40.508766+00	140.213.117.217	Gathering	attendances/40/check_out/2025-12-05/131dc134-9fca-4eb4-870d-ec00ee8f7bbb.jpeg	2025-12-05 00:06:48.247131+00	2025-12-05 15:02:41.335385+00	-5.38759456	105.28016691	Jalan Alam Kurnia, Kalibalau Kencana, Bandar Lampung, Lampung, Sumatra, 35133, Indonesia	-5.68574264	105.22742377	Pulau Pahawang, Pesawaran, Lampung, Sumatra, Indonesia	0.00
768	39	32	2025-12-05	present	2025-12-05 15:13:11.618974+00	2025-12-05 15:13:33.885989+00	0.01	39	2025-12-05 15:13:11.618974+00	140.213.112.61	\N	attendances/39/check_in/2025-12-05/f52bd99e-30ff-40d2-bd05-d7c18efdf05e.jpeg	2025-12-05 15:13:33.885989+00	140.213.112.61	\N	attendances/39/check_out/2025-12-05/66b1f77d-0d25-4570-8d4d-9fe47e474b30.jpeg	2025-12-05 15:13:12.798672+00	2025-12-05 15:13:34.654195+00	-5.68551620	105.22740160	Pulau Pahawang, Pesawaran, Lampung, Sumatra, Indonesia	-5.68551620	105.22740160	Pulau Pahawang, Pesawaran, Lampung, Sumatra, Indonesia	0.00
892	49	23	2025-12-09	absent	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	2025-12-09 16:00:00.058912+00	2025-12-09 16:00:00.058917+00	\N	\N	\N	\N	\N	\N	\N
897	62	30	2025-12-09	absent	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	2025-12-09 16:00:00.087028+00	2025-12-09 16:00:00.087031+00	\N	\N	\N	\N	\N	\N	\N
902	58	27	2025-12-09	absent	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	2025-12-09 16:00:00.109544+00	2025-12-09 16:00:00.109548+00	\N	\N	\N	\N	\N	\N	\N
907	64	24	2025-12-09	absent	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	2025-12-09 16:00:00.143435+00	2025-12-09 16:00:00.143461+00	\N	\N	\N	\N	\N	\N	\N
790	15	21	2025-12-05	absent	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	2025-12-05 16:00:00.232712+00	2025-12-05 16:00:00.232717+00	\N	\N	\N	\N	\N	\N	\N
762	42	28	2025-12-05	invalid	2025-12-04 23:55:05.944877+00	\N	\N	42	2025-12-04 23:55:05.944877+00	103.105.82.245	\N	attendances/42/check_in/2025-12-05/7e7dcc09-c1d2-457c-a6b6-db3da73a39c9.jpeg	\N	\N	\N	\N	2025-12-04 23:55:07.078976+00	2025-12-05 16:30:00.052994+00	-5.38758180	105.28016050	Jalan Alam Cantik, Kalibalau Kencana, Bandar Lampung, Lampung, Sumatra, 35133, Indonesia	\N	\N	\N	\N
766	41	21	2025-12-05	invalid	2025-12-05 00:40:25.480953+00	\N	\N	41	2025-12-05 00:40:25.480953+00	114.10.102.10	\N	attendances/41/check_in/2025-12-05/aa50771d-edcc-447a-8d51-973bd0d7af96.jpeg	\N	\N	\N	\N	2025-12-05 00:40:26.593238+00	2025-12-05 16:30:00.053671+00	-5.39324008	105.28153365	Jalan Arif Rahman Hakim, Kalibalau Kencana, Bandar Lampung, Lampung, Sumatra, 35133, Indonesia	\N	\N	\N	\N
912	24	31	2025-12-10	present	2025-12-10 01:46:25.325126+00	2025-12-10 10:52:50.603311+00	9.11	24	2025-12-10 01:46:25.325126+00	103.105.82.245	\N	attendances/24/check_in/2025-12-10/29714d40-5810-4049-9d03-16e4ba0ea3d0.jpeg	2025-12-10 10:52:50.603311+00	103.105.82.245	\N	attendances/24/check_out/2025-12-10/dbc56c2d-eb4c-4fb4-8bab-83bdcf435136.jpeg	2025-12-10 01:46:26.364731+00	2025-12-10 10:52:51.352697+00	-5.38757270	105.28013690	Jalan Alam Kurnia, Kalibalau Kencana, Bandar Lampung, Lampung, Sumatra, 35133, Indonesia	-5.38757240	105.28017520	Jalan Alam Cantik, Kalibalau Kencana, Bandar Lampung, Lampung, Sumatra, 35133, Indonesia	0.00
913	20	31	2025-12-10	invalid	2025-12-10 01:55:19.428024+00	\N	\N	20	2025-12-10 01:55:19.428024+00	103.105.82.245	\N	attendances/20/check_in/2025-12-10/d545516a-9378-4d9e-9161-7dbd87e006a3.jpeg	\N	\N	\N	\N	2025-12-10 01:55:20.436015+00	2025-12-10 16:30:00.048003+00	-5.38763062	105.28006228	Jalan Alam Kurnia, Kalibalau Kencana, Bandar Lampung, Lampung, Sumatra, 35133, Indonesia	\N	\N	\N	\N
1142	50	23	2025-12-17	present	2025-12-17 03:18:18.817819+00	2025-12-17 11:51:46.278664+00	8.56	50	2025-12-17 03:18:18.817819+00	114.10.100.17	\N	attendances/50/check_in/2025-12-17/3367c3c8-d16f-48df-8144-ded797d6caae.jpeg	2025-12-17 11:51:46.278664+00	114.10.100.17	\N	attendances/50/check_out/2025-12-17/c75b1675-d889-445a-9d2d-f83bea0a5e4b.jpeg	2025-12-17 03:18:19.874408+00	2025-12-17 11:51:48.029337+00	-5.35933220	104.78049050	Jalan Talang Padang - Ngarip, Sinar Semendo, Tanggamus, Lampung, Sumatra, Indonesia	-5.42945170	104.73420170	Gisting Bawah, Tanggamus, Lampung, Sumatra, Indonesia	0.00
121	43	17	2025-11-10	hybrid	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	2025-11-10 16:00:00.863325+00	2025-11-10 16:00:00.86333+00	\N	\N	\N	\N	\N	\N	\N
765	43	32	2025-12-05	present	2025-12-05 00:33:41.392741+00	2025-12-05 15:02:28.571128+00	14.48	43	2025-12-05 00:33:41.392741+00	182.3.73.182	\N	attendances/43/check_in/2025-12-05/caf3996d-c4da-43a5-9674-cb37e5167ebe.jpeg	2025-12-05 15:02:28.571128+00	140.213.120.40	\N	attendances/43/check_out/2025-12-05/343ae42f-d3b9-41cd-8929-3288bc47f47e.jpeg	2025-12-05 00:33:42.56825+00	2025-12-05 15:02:30.103292+00	-5.38762360	105.28014810	Jalan Alam Kurnia, Kalibalau Kencana, Bandar Lampung, Lampung, Sumatra, 35133, Indonesia	-5.68585640	105.22726840	Pulau Pahawang, Pesawaran, Lampung, Sumatra, Indonesia	0.00
151	39	17	2025-11-11	hybrid	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	2025-11-11 16:00:01.267385+00	2025-11-11 16:00:01.267391+00	\N	\N	\N	\N	\N	\N	\N
125	42	11	2025-11-11	invalid	2025-11-11 00:57:50.091992+00	\N	\N	42	2025-11-11 00:57:50.091992+00	182.3.104.89	\N	attendances/42/check_in/2025-11-11/e542ad85-89a2-40cb-9956-d44f2503db10.jpeg	\N	\N	\N	\N	2025-11-11 00:57:51.141301+00	2025-11-11 16:59:00.072075+00	-5.24293940	105.17608810	Jalan Lintas Tengah Sumatera, Bumisari, Lampung Selatan, Lampung, Sumatra, Indonesia	\N	\N	\N	\N
778	62	30	2025-12-05	absent	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	2025-12-05 16:00:00.157904+00	2025-12-05 16:00:00.157909+00	\N	\N	\N	\N	\N	\N	\N
916	14	28	2025-12-10	present	2025-12-10 02:27:44.539846+00	2025-12-10 13:10:19.299282+00	10.71	14	2025-12-10 02:27:44.539846+00	103.105.82.245	\N	attendances/14/check_in/2025-12-10/a15dcea8-5600-4706-ba85-5a500af0dfed.jpeg	2025-12-10 13:10:19.299282+00	182.3.73.76	\N	attendances/14/check_out/2025-12-10/9fd2ecef-a779-481c-ac2b-cac8249490f0.jpeg	2025-12-10 02:27:45.542514+00	2025-12-10 13:10:20.73381+00	-5.38070920	105.26996230	Perumnas Way Halim, Bandar Lampung, Lampung, Sumatra, 35132, Indonesia	-5.40676000	105.19750330	Sumber Rejo, Bandar Lampung, Lampung, Sumatra, 35158, Indonesia	0.00
1141	15	21	2025-12-17	present	2025-12-17 03:01:19.39443+00	2025-12-17 09:30:00.430321+00	6.48	15	2025-12-17 03:01:19.39443+00	182.3.100.183	\N	attendances/15/check_in/2025-12-17/ef258580-355b-42c2-8009-89dd2afb7cc1.jpeg	2025-12-17 09:30:00.430321+00	103.105.82.243	\N	attendances/15/check_out/2025-12-17/d10716bd-2673-4ecd-8331-cb19362a63e8.jpeg	2025-12-17 03:01:20.535139+00	2025-12-17 09:30:01.460156+00	-5.38758550	105.28015490	Jalan Alam Kurnia, Kalibalau Kencana, Bandar Lampung, Lampung, Sumatra, 35133, Indonesia	-5.38758550	105.28015490	Jalan Alam Kurnia, Kalibalau Kencana, Bandar Lampung, Lampung, Sumatra, 35133, Indonesia	0.00
763	24	31	2025-12-05	invalid	2025-12-04 23:55:25.263958+00	\N	\N	24	2025-12-04 23:55:25.263958+00	103.105.82.245	\N	attendances/24/check_in/2025-12-05/d43c560e-93ec-465b-aeee-2672b1df7b8d.jpeg	\N	\N	\N	\N	2025-12-04 23:55:25.981743+00	2025-12-05 16:30:00.054227+00	-5.38758210	105.28016130	Jalan Alam Cantik, Kalibalau Kencana, Bandar Lampung, Lampung, Sumatra, 35133, Indonesia	\N	\N	\N	\N
1145	55	27	2025-12-17	present	2025-12-17 10:02:26.795024+00	2025-12-17 10:03:08.071581+00	0.01	55	2025-12-17 10:02:26.795024+00	114.10.98.207	Pagaralam	attendances/55/check_in/2025-12-17/81e82a84-f44e-4e7f-af7e-a055f3fe461c.jpeg	2025-12-17 10:03:08.071581+00	114.10.98.207	pagaralam	attendances/55/check_out/2025-12-17/45bd129c-9d83-42f5-a951-cb29640df357.jpeg	2025-12-17 10:02:27.619105+00	2025-12-17 10:03:09.946277+00	-4.05596750	103.29801560	Rantau Unji, Dempo Tengah, Pagar Alam, Sumatera Selatan, Sumatra, Indonesia	-4.05596750	103.29801560	Rantau Unji, Dempo Tengah, Pagar Alam, Sumatera Selatan, Sumatra, Indonesia	0.00
1147	59	29	2025-12-17	absent	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	2025-12-17 16:00:00.338757+00	2025-12-17 16:00:00.338762+00	\N	\N	\N	\N	\N	\N	\N
1151	40	28	2025-12-17	absent	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	2025-12-17 16:00:00.41889+00	2025-12-17 16:00:00.418895+00	\N	\N	\N	\N	\N	\N	\N
1155	49	23	2025-12-18	present	2025-12-18 01:23:12.915717+00	\N	\N	49	2025-12-18 01:23:12.915717+00	103.59.44.25	\N	attendances/49/check_in/2025-12-18/444176bf-4abf-4b38-9c97-84cfc87e14ec.jpeg	\N	\N	\N	\N	2025-12-18 01:23:13.984008+00	2025-12-18 01:23:13.984012+00	-5.43041000	104.73893670	Gisting Bawah, Tanggamus, Lampung, Sumatra, Indonesia	\N	\N	\N	\N
1161	55	27	2025-12-18	present	2025-12-18 01:51:28.853368+00	\N	\N	55	2025-12-18 01:51:28.853368+00	114.10.98.207	Pagaralam	attendances/55/check_in/2025-12-18/d04203d8-6e3d-4575-afe6-1e432e0fe956.jpeg	\N	\N	\N	\N	2025-12-18 01:51:29.589623+00	2025-12-18 01:51:29.589627+00	-4.05607110	103.29807080	Rantau Unji, Dempo Tengah, Pagar Alam, Sumatera Selatan, Sumatra, Indonesia	\N	\N	\N	\N
1165	63	25	2025-12-18	present	2025-12-18 02:10:36.943325+00	\N	\N	63	2025-12-18 02:10:36.943325+00	114.10.102.177	\N	attendances/63/check_in/2025-12-18/3fab81f9-18d3-42a8-ae05-72205ec2ca52.jpeg	\N	\N	\N	\N	2025-12-18 02:10:37.704901+00	2025-12-18 02:10:37.704906+00	-5.02823030	104.30404570	Jalan Raya Serengit, Mekar Sari, Lampung Barat, Lampung, Sumatra, Indonesia	\N	\N	\N	\N
1166	42	28	2025-12-18	present	2025-12-18 02:20:26.240141+00	\N	\N	42	2025-12-18 02:20:26.240141+00	103.105.82.243	\N	attendances/42/check_in/2025-12-18/59da1007-6367-4a26-b3ec-ccba989d2991.jpeg	\N	\N	\N	\N	2025-12-18 02:20:27.217199+00	2025-12-18 02:20:27.217203+00	-5.38758300	105.28016380	Jalan Alam Cantik, Kalibalau Kencana, Bandar Lampung, Lampung, Sumatra, 35133, Indonesia	\N	\N	\N	\N
1173	47	22	2025-12-18	present	2025-12-18 03:39:55.446331+00	\N	\N	47	2025-12-18 03:39:55.446331+00	103.59.44.25	visit gudang gisting	attendances/47/check_in/2025-12-18/f1e5f12d-eaee-4a0f-b814-db68017f11f1.jpeg	\N	\N	\N	\N	2025-12-18 03:39:56.523631+00	2025-12-18 03:39:56.523636+00	-5.43048700	104.73907620	Gisting Bawah, Tanggamus, Lampung, Sumatra, Indonesia	\N	\N	\N	\N
122	44	17	2025-11-10	absent	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	2025-11-10 16:00:00.869471+00	2025-11-10 16:00:00.869475+00	\N	\N	\N	\N	\N	\N	\N
767	44	34	2025-12-05	present	2025-12-05 02:19:57.674464+00	2025-12-05 12:16:39.154422+00	9.94	44	2025-12-05 02:19:57.674464+00	114.10.102.69	\N	attendances/44/check_in/2025-12-05/a65caed8-837e-4394-b979-4870c12e5216.jpeg	2025-12-05 12:16:39.154422+00	114.10.102.69	\N	attendances/44/check_out/2025-12-05/ed3c6897-a93d-4c9c-8c86-177dc3ba55fe.jpeg	2025-12-05 02:19:59.196156+00	2025-12-05 12:16:40.154973+00	-5.37269620	105.24937710	Gang Zakaria III, Sepang Jaya, Bandar Lampung, Lampung, Sumatra, 35148, Indonesia	-5.37162360	105.25074850	Gang Zakaria IV, Sepang Jaya, Bandar Lampung, Lampung, Sumatra, 35141, Indonesia	0.00
769	13	20	2025-12-05	absent	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	2025-12-05 16:00:00.066217+00	2025-12-05 16:00:00.066223+00	\N	\N	\N	\N	\N	\N	\N
779	22	33	2025-12-05	absent	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	2025-12-05 16:00:00.163122+00	2025-12-05 16:00:00.163126+00	\N	\N	\N	\N	\N	\N	\N
917	22	33	2025-12-10	present	2025-12-10 02:35:54.421481+00	2025-12-10 15:03:10.292395+00	12.45	22	2025-12-10 02:35:54.421481+00	103.105.82.245	\N	attendances/22/check_in/2025-12-10/1e739d07-e871-4d9d-aafb-ef43b900688b.jpeg	2025-12-10 15:03:10.292395+00	36.68.127.149	\N	attendances/22/check_out/2025-12-10/4bc2dfa7-7cf1-4fb9-bb13-18acf0f70279.jpeg	2025-12-10 02:35:55.557659+00	2025-12-10 15:03:11.387981+00	-5.38758060	105.28016070	Jalan Alam Cantik, Kalibalau Kencana, Bandar Lampung, Lampung, Sumatra, 35133, Indonesia	-5.37421230	105.24272970	Jalan Zainal Abidin Pagar Alam, Pelita, Bandar Lampung, Lampung, Sumatra, 35142, Indonesia	0.00
1137	57	27	2025-12-17	present	2025-12-17 02:41:31.087478+00	2025-12-17 10:02:07.469042+00	7.34	57	2025-12-17 02:41:31.087478+00	180.242.4.50	\N	attendances/57/check_in/2025-12-17/25b9adae-fc62-4b66-90c4-b18620d75c7c.jpeg	2025-12-17 10:02:07.469042+00	203.78.120.172	\N	attendances/57/check_out/2025-12-17/7ab1016f-4299-4bcf-8ca7-e531367edeff.jpeg	2025-12-17 02:41:32.14798+00	2025-12-17 10:02:09.367294+00	-4.05600612	103.29804352	Rantau Unji, Dempo Tengah, Pagar Alam, Sumatera Selatan, Sumatra, Indonesia	-4.05608138	103.29802366	Rantau Unji, Dempo Tengah, Pagar Alam, Sumatera Selatan, Sumatra, Indonesia	0.00
1146	46	21	2025-12-17	absent	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	2025-12-17 16:00:00.271108+00	2025-12-17 16:00:00.271116+00	\N	\N	\N	\N	\N	\N	\N
1150	20	31	2025-12-17	absent	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	2025-12-17 16:00:00.411432+00	2025-12-17 16:00:00.411455+00	\N	\N	\N	\N	\N	\N	\N
1158	48	23	2025-12-18	present	2025-12-18 01:43:30.462015+00	\N	\N	48	2025-12-18 01:43:30.462015+00	103.133.61.135	Mau ambil raport Anak Anak	attendances/48/check_in/2025-12-18/57c8e47f-554a-4511-98a6-532b123b7614.jpeg	\N	\N	\N	\N	2025-12-18 01:43:31.171016+00	2025-12-18 01:43:31.171019+00	-5.34646940	105.02571530	Jogyakarta, Pringsewu, Lampung, Sumatra, Indonesia	\N	\N	\N	\N
1167	57	27	2025-12-18	present	2025-12-18 02:21:00.674853+00	\N	\N	57	2025-12-18 02:21:00.674853+00	103.144.14.2	\N	attendances/57/check_in/2025-12-18/2546f19d-edbd-4604-ad06-82814414aa69.jpeg	\N	\N	\N	\N	2025-12-18 02:21:01.505413+00	2025-12-18 02:21:01.505419+00	-4.05605981	103.29799423	Rantau Unji, Dempo Tengah, Pagar Alam, Sumatera Selatan, Sumatra, Indonesia	\N	\N	\N	\N
1168	40	28	2025-12-18	present	2025-12-18 02:28:17.943155+00	\N	\N	40	2025-12-18 02:28:17.943155+00	103.105.82.243	\N	attendances/40/check_in/2025-12-18/0608022f-a10b-4743-9bdf-1589a863f087.jpeg	\N	\N	\N	\N	2025-12-18 02:28:19.021179+00	2025-12-18 02:28:19.021183+00	-5.37820700	105.27800970	Masjid Daarul Ukhuwah, Perumnas Way Halim, Way Halim Permai, Bandar Lampung, Lampung, Sumatra, 35133, Indonesia	\N	\N	\N	\N
1170	44	34	2025-12-18	present	2025-12-18 02:39:49.085028+00	\N	\N	44	2025-12-18 02:39:49.085028+00	114.10.102.43	\N	attendances/44/check_in/2025-12-18/0f0bc3a8-0876-43b4-92fa-4ea487387899.jpeg	\N	\N	\N	\N	2025-12-18 02:39:50.111262+00	2025-12-18 02:39:50.111266+00	-5.36712720	105.24644840	Universitas Lampung UNILA, Jalan Bypass Sukarno Hatta, Bandar Lampung, Lampung Selatan, Lampung, Sumatra, 35144, Indonesia	\N	\N	\N	\N
1171	50	23	2025-12-18	present	2025-12-18 02:45:47.119991+00	\N	\N	50	2025-12-18 02:45:47.119991+00	114.10.102.20	\N	attendances/50/check_in/2025-12-18/83852e34-46d2-46fb-b933-44cb643875cf.jpeg	\N	\N	\N	\N	2025-12-18 02:45:48.182975+00	2025-12-18 02:45:48.182978+00	-5.42870640	104.73368220	Gisting Bawah, Tanggamus, Lampung, Sumatra, Indonesia	\N	\N	\N	\N
1174	39	32	2025-12-18	present	2025-12-18 04:41:39.20801+00	\N	\N	39	2025-12-18 04:41:39.20801+00	103.105.82.243	\N	attendances/39/check_in/2025-12-18/4e2bd014-be1f-40ba-8594-c365df1a0377.jpeg	\N	\N	\N	\N	2025-12-18 04:41:40.459766+00	2025-12-18 04:41:40.45977+00	-5.38758240	105.28014930	Jalan Alam Kurnia, Kalibalau Kencana, Bandar Lampung, Lampung, Sumatra, 35133, Indonesia	\N	\N	\N	\N
918	41	21	2025-12-10	present	2025-12-10 02:44:23.505963+00	2025-12-10 10:50:15.522619+00	8.10	41	2025-12-10 02:44:23.505963+00	103.105.82.245	\N	attendances/41/check_in/2025-12-10/b16d50a0-e8ea-4232-9165-e0b996e1198f.jpeg	2025-12-10 10:50:15.522619+00	103.105.82.245	\N	attendances/41/check_out/2025-12-10/95910fff-31f1-4807-a734-9c4a51bb1257.jpeg	2025-12-10 02:44:24.600207+00	2025-12-10 10:50:17.617476+00	-5.38757310	105.28013640	Jalan Alam Kurnia, Kalibalau Kencana, Bandar Lampung, Lampung, Sumatra, 35133, Indonesia	-5.38754852	105.28020646	Jalan Alam Cantik, Kalibalau Kencana, Bandar Lampung, Lampung, Sumatra, 35133, Indonesia	0.00
786	14	28	2025-12-05	absent	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	2025-12-05 16:00:00.202692+00	2025-12-05 16:00:00.202696+00	\N	\N	\N	\N	\N	\N	\N
152	43	17	2025-11-11	hybrid	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	2025-11-11 16:00:01.288761+00	2025-11-11 16:00:01.288766+00	\N	\N	\N	\N	\N	\N	\N
124	41	12	2025-11-11	invalid	2025-11-11 00:51:11.655253+00	\N	\N	41	2025-11-11 00:51:11.655253+00	182.3.104.63	\N	attendances/41/check_in/2025-11-11/27618e26-5175-4448-b9cc-c607c742fc8a.jpeg	\N	\N	\N	\N	2025-11-11 00:51:12.672943+00	2025-11-11 16:59:00.073925+00	-5.24054240	105.17465420	Jalan Lintas Tengah Sumatera, Bumisari, Lampung Selatan, Lampung, Sumatra, Indonesia	\N	\N	\N	\N
919	44	34	2025-12-10	present	2025-12-10 02:53:56.215259+00	2025-12-10 14:18:55.437893+00	11.42	44	2025-12-10 02:53:56.215259+00	182.3.102.105	\N	attendances/44/check_in/2025-12-10/84be5cf1-f4b6-45e2-bf61-12f23a3cd74e.jpeg	2025-12-10 14:18:55.437893+00	182.3.105.151	\N	attendances/44/check_out/2025-12-10/86937afc-2a08-47fe-a840-d1236374a6ff.jpeg	2025-12-10 02:53:57.174023+00	2025-12-10 14:18:56.665629+00	-5.38758480	105.28015870	Jalan Alam Kurnia, Kalibalau Kencana, Bandar Lampung, Lampung, Sumatra, 35133, Indonesia	-5.31187180	104.55612200	Pagaralam Ulubelu, Tanggamus, Lampung, Sumatra, Indonesia	0.00
1139	48	23	2025-12-17	present	2025-12-17 02:45:18.716813+00	2025-12-17 10:21:20.457318+00	7.60	48	2025-12-17 02:45:18.716813+00	182.3.103.195	Visit ke gudang mas nur pardasuka	attendances/48/check_in/2025-12-17/cdc0f587-12e2-4875-be94-00eb1289f035.jpeg	2025-12-17 10:21:20.457318+00	103.133.61.135	\N	attendances/48/check_out/2025-12-17/a8c8b62a-5b11-4a74-8e4d-2df2b10e3d50.jpeg	2025-12-17 02:45:19.450645+00	2025-12-17 10:21:21.436459+00	-5.37218670	104.96571830	Jalan Pringsewu - Pardasuka, Pringsewu, Lampung, Sumatra, 35373, Indonesia	-5.34647500	105.02570150	Jogyakarta, Pringsewu, Lampung, Sumatra, Indonesia	0.00
1136	42	28	2025-12-17	present	2025-12-17 02:26:07.444035+00	2025-12-17 10:30:42.323898+00	8.08	42	2025-12-17 02:26:07.444035+00	103.105.82.243	\N	attendances/42/check_in/2025-12-17/7bfa487e-9784-4aa1-b258-1ba80fda3eb4.jpeg	2025-12-17 10:30:42.323898+00	103.105.82.243	\N	attendances/42/check_out/2025-12-17/23e0c7e5-b640-4f61-af66-e98d75be19d5.jpeg	2025-12-17 02:26:08.155059+00	2025-12-17 10:30:43.527084+00	-5.38758490	105.28015890	Jalan Alam Kurnia, Kalibalau Kencana, Bandar Lampung, Lampung, Sumatra, 35133, Indonesia	-5.38757400	105.28013670	Jalan Alam Kurnia, Kalibalau Kencana, Bandar Lampung, Lampung, Sumatra, 35133, Indonesia	0.00
1148	56	27	2025-12-17	absent	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	2025-12-17 16:00:00.364961+00	2025-12-17 16:00:00.364966+00	\N	\N	\N	\N	\N	\N	\N
1152	43	32	2025-12-17	hybrid	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	2025-12-17 16:00:00.430418+00	2025-12-17 16:00:00.430423+00	\N	\N	\N	\N	\N	\N	\N
1160	54	25	2025-12-18	present	2025-12-18 01:50:30.091379+00	\N	\N	54	2025-12-18 01:50:30.091379+00	103.87.231.107	\N	attendances/54/check_in/2025-12-18/8c5f10e2-dbf4-402d-b9f0-0c294b736af7.jpeg	\N	\N	\N	\N	2025-12-18 01:50:31.133117+00	2025-12-18 01:50:31.133121+00	-5.02823000	104.30404500	Jalan Raya Serengit, Mekar Sari, Lampung Barat, Lampung, Sumatra, Indonesia	\N	\N	\N	\N
1162	23	33	2025-12-18	present	2025-12-18 01:57:28.622255+00	\N	\N	23	2025-12-18 01:57:28.622255+00	103.105.82.243	\N	attendances/23/check_in/2025-12-18/853a2179-7a2d-4ee9-a33d-3727c24514de.jpeg	\N	\N	\N	\N	2025-12-18 01:57:29.668124+00	2025-12-18 01:57:29.668127+00	-5.38757581	105.28020450	Jalan Alam Cantik, Kalibalau Kencana, Bandar Lampung, Lampung, Sumatra, 35133, Indonesia	\N	\N	\N	\N
1164	53	25	2025-12-18	present	2025-12-18 02:09:10.032532+00	\N	\N	53	2025-12-18 02:09:10.032532+00	114.10.100.206	\N	attendances/53/check_in/2025-12-18/bd8b8051-49eb-4520-b04d-46ca182af66a.jpeg	\N	\N	\N	\N	2025-12-18 02:09:10.77922+00	2025-12-18 02:09:10.779224+00	-5.02815560	104.30406730	Jalan Raya Serengit, Mekar Sari, Lampung Barat, Lampung, Sumatra, Indonesia	\N	\N	\N	\N
1169	41	21	2025-12-18	present	2025-12-18 02:37:39.111675+00	\N	\N	41	2025-12-18 02:37:39.111675+00	103.105.82.243	\N	attendances/41/check_in/2025-12-18/dac6b843-d4bc-4326-a601-a25fdbc5bd01.jpeg	\N	\N	\N	\N	2025-12-18 02:37:40.001612+00	2025-12-18 02:37:40.001617+00	-5.38757132	105.28019278	Jalan Alam Cantik, Kalibalau Kencana, Bandar Lampung, Lampung, Sumatra, 35133, Indonesia	\N	\N	\N	\N
128	24	15	2025-11-11	present	2025-11-11 02:41:44.263998+00	2025-11-11 10:08:10.000142+00	7.44	24	2025-11-11 02:41:44.263998+00	182.253.63.30	\N	attendances/24/check_in/2025-11-11/bbaaa211-fcdf-487f-ae47-fa6f3ee8b69a.jpeg	2025-11-11 10:08:10.000142+00	182.253.63.30	\N	attendances/24/check_out/2025-11-11/68d2e8dc-1615-4c78-8eae-2925cab323c5.jpeg	2025-11-11 02:41:45.324878+00	2025-11-11 10:08:11.52132+00	-5.40344320	105.27047680	Jagabaya III, Bandar Lampung, Lampung, Sumatra, 35227, Indonesia	-5.36358130	105.28166770	Way Dadi, Bandar Lampung, Lampung, Sumatra, 35139, Indonesia	\N
126	40	11	2025-11-11	present	2025-11-11 01:45:40.093606+00	2025-11-11 10:37:44.091958+00	8.87	40	2025-11-11 01:45:40.093606+00	182.253.63.30	\N	attendances/40/check_in/2025-11-11/e89c19ce-5d4c-4d90-b7b4-5efc05fa5b8a.jpeg	2025-11-11 10:37:44.091958+00	182.253.63.30	\N	attendances/40/check_out/2025-11-11/565f50f2-668c-45f2-9516-24fae3e112a9.jpeg	2025-11-11 01:45:41.332659+00	2025-11-11 10:37:45.368891+00	-5.38754325	105.28013186	Jalan Alam Cantik, Kalibalau Kencana, Bandar Lampung, Lampung, Sumatra, 35133, Indonesia	-5.38758200	105.28016830	Jalan Alam Cantik, Kalibalau Kencana, Bandar Lampung, Lampung, Sumatra, 35133, Indonesia	\N
920	56	27	2025-12-10	present	2025-12-10 07:18:42.678186+00	2025-12-10 07:19:51.118995+00	0.02	56	2025-12-10 07:18:42.678186+00	182.1.237.74	Pagar alam	attendances/56/check_in/2025-12-10/d3f090dc-7568-4a5f-bb1e-6618b3e02496.jpeg	2025-12-10 07:19:51.118995+00	182.1.237.74	\N	attendances/56/check_out/2025-12-10/0558b7d1-155e-46d7-b371-cd0731eb05ad.jpeg	2025-12-10 07:18:44.099215+00	2025-12-10 07:19:52.008517+00	-4.05606540	103.29807060	Rantau Unji, Dempo Tengah, Pagar Alam, Sumatera Selatan, Sumatra, Indonesia	-4.05606380	103.29807010	Rantau Unji, Dempo Tengah, Pagar Alam, Sumatera Selatan, Sumatra, Indonesia	0.00
123	15	12	2025-11-11	invalid	2025-11-11 00:39:11.840991+00	\N	\N	15	2025-11-11 00:39:11.840991+00	182.3.105.83	\N	attendances/15/check_in/2025-11-11/e3c56a3a-999f-45dd-9203-d0a451581a70.jpeg	\N	\N	\N	\N	2025-11-11 00:39:13.346939+00	2025-11-11 16:59:00.075458+00	-5.24180450	105.17510860	Jalan Lintas Tengah Sumatera, Bumisari, Lampung Selatan, Lampung, Sumatra, Indonesia	\N	\N	\N	\N
162	39	17	2025-11-12	present	2025-11-12 03:20:54.410313+00	2025-11-12 09:09:28.73354+00	5.81	39	2025-11-12 03:20:54.410313+00	182.253.63.30	\N	attendances/39/check_in/2025-11-12/cf996c2c-6c47-4b14-807d-6c193fa13538.jpeg	2025-11-12 09:09:28.73354+00	182.253.63.30	\N	attendances/39/check_out/2025-11-12/5df26851-612f-46c6-85e9-980a4efed60e.jpeg	2025-11-12 03:20:56.288747+00	2025-11-12 09:09:29.996157+00	-5.38757960	105.28016190	Jalan Alam Cantik, Kalibalau Kencana, Bandar Lampung, Lampung, Sumatra, 35133, Indonesia	-5.38758090	105.28016510	Jalan Alam Cantik, Kalibalau Kencana, Bandar Lampung, Lampung, Sumatra, 35133, Indonesia	\N
160	14	11	2025-11-12	present	2025-11-12 02:58:12.167742+00	2025-11-12 10:41:26.15324+00	7.72	14	2025-11-12 02:58:12.167742+00	182.253.63.30	\N	attendances/14/check_in/2025-11-12/17f05913-72f0-4d6c-bdd4-f4e0ee8b70aa.jpeg	2025-11-12 10:41:26.15324+00	182.253.63.30	\N	attendances/14/check_out/2025-11-12/73e1eff0-f0af-4cdb-ba41-487b4e7086b7.jpeg	2025-11-12 02:58:13.173762+00	2025-11-12 10:41:27.362503+00	-5.36358130	105.28166770	Way Dadi, Bandar Lampung, Lampung, Sumatra, 35139, Indonesia	-5.36358130	105.28166770	Way Dadi, Bandar Lampung, Lampung, Sumatra, 35139, Indonesia	\N
153	40	11	2025-11-12	present	2025-11-12 01:11:15.186523+00	2025-11-12 10:43:43.490011+00	9.54	40	2025-11-12 01:11:15.186523+00	182.253.63.30	\N	attendances/40/check_in/2025-11-12/19767c3b-0b98-48ae-804a-a8efb9b91330.jpeg	2025-11-12 10:43:43.490011+00	182.253.63.30	\N	attendances/40/check_out/2025-11-12/2f536387-ba61-4264-953e-7ce5e5c5bc28.jpeg	2025-11-12 01:11:16.949957+00	2025-11-12 10:43:44.277014+00	-5.38753078	105.28022572	Jalan Alam Cantik, Kalibalau Kencana, Bandar Lampung, Lampung, Sumatra, 35133, Indonesia	-5.36358130	105.28166770	Way Dadi, Bandar Lampung, Lampung, Sumatra, 35139, Indonesia	\N
163	22	15	2025-11-12	present	2025-11-12 08:04:32.256693+00	2025-11-12 11:26:05.299497+00	3.36	22	2025-11-12 08:04:32.256693+00	182.253.63.30	\N	attendances/22/check_in/2025-11-12/42df23db-b806-4b51-8c8b-96c8a79df89c.jpeg	2025-11-12 11:26:05.299497+00	182.253.63.30	\N	attendances/22/check_out/2025-11-12/a5b252a0-3bd6-412f-89a3-f7ebfce8f713.jpeg	2025-11-12 08:04:34.065263+00	2025-11-12 11:26:06.652695+00	-5.37693280	105.27362020	Jalan Gunung Rajabasa Raya, Harapan Jaya, Bandar Lampung, Lampung, Sumatra, 35133, Indonesia	-5.37693280	105.27362020	Jalan Gunung Rajabasa Raya, Harapan Jaya, Bandar Lampung, Lampung, Sumatra, 35133, Indonesia	\N
156	42	11	2025-11-12	present	2025-11-12 02:02:16.98088+00	2025-11-12 11:26:05.870014+00	9.40	42	2025-11-12 02:02:16.98088+00	182.3.101.237	\N	attendances/42/check_in/2025-11-12/6740d757-4811-4f83-bd74-22fc94784718.jpeg	2025-11-12 11:26:05.870014+00	182.253.63.30	\N	attendances/42/check_out/2025-11-12/1e3bc36b-185e-40f8-923d-3f88621c948b.jpeg	2025-11-12 02:02:18.158569+00	2025-11-12 11:26:07.588962+00	-5.02823640	104.30406300	Jalan Raya Serengit, Mekar Sari, Lampung Barat, Lampung, Sumatra, Indonesia	-5.38759060	105.28016020	Jalan Alam Kurnia, Kalibalau Kencana, Bandar Lampung, Lampung, Sumatra, 35133, Indonesia	\N
154	23	15	2025-11-12	present	2025-11-12 01:30:48.330596+00	2025-11-12 11:26:22.97912+00	9.93	23	2025-11-12 01:30:48.330596+00	182.253.63.30	\N	attendances/23/check_in/2025-11-12/7476b0b1-1642-4e39-bb38-e8a1163f6f9f.jpeg	2025-11-12 11:26:22.97912+00	182.253.63.30	\N	attendances/23/check_out/2025-11-12/11faef06-991b-42fc-8060-f94a58c24817.jpeg	2025-11-12 01:30:49.555244+00	2025-11-12 11:26:23.793571+00	-5.38753521	105.28017974	Jalan Alam Cantik, Kalibalau Kencana, Bandar Lampung, Lampung, Sumatra, 35133, Indonesia	-5.38756038	105.28019496	Jalan Alam Cantik, Kalibalau Kencana, Bandar Lampung, Lampung, Sumatra, 35133, Indonesia	\N
158	24	15	2025-11-12	present	2025-11-12 02:17:01.83469+00	2025-11-12 11:26:43.393673+00	9.16	24	2025-11-12 02:17:01.83469+00	182.253.63.30	\N	attendances/24/check_in/2025-11-12/7c34450d-4945-4c9d-b80b-63c99499d6d8.jpeg	2025-11-12 11:26:43.393673+00	182.253.63.30	\N	attendances/24/check_out/2025-11-12/081686d0-b094-4cbe-ad47-28f8c169895f.jpeg	2025-11-12 02:17:02.852727+00	2025-11-12 11:26:44.163734+00	-5.36358130	105.28166770	Way Dadi, Bandar Lampung, Lampung, Sumatra, 35139, Indonesia	-5.37693280	105.27362020	Jalan Gunung Rajabasa Raya, Harapan Jaya, Bandar Lampung, Lampung, Sumatra, 35133, Indonesia	\N
157	44	17	2025-11-12	present	2025-11-12 02:07:10.550498+00	2025-11-12 11:27:50.042485+00	9.34	44	2025-11-12 02:07:10.550498+00	182.253.63.30	\N	attendances/44/check_in/2025-11-12/c53e2223-6111-4a30-8945-14cd8df3b416.jpeg	2025-11-12 11:27:50.042485+00	114.10.100.197	\N	attendances/44/check_out/2025-11-12/b26a916c-0b26-4157-ab41-c00a20a21be5.jpeg	2025-11-12 02:07:11.571127+00	2025-11-12 11:27:50.762849+00	-5.38758420	105.28016320	Jalan Alam Cantik, Kalibalau Kencana, Bandar Lampung, Lampung, Sumatra, 35133, Indonesia	-5.38758190	105.28016340	Jalan Alam Cantik, Kalibalau Kencana, Bandar Lampung, Lampung, Sumatra, 35133, Indonesia	\N
155	41	12	2025-11-12	present	2025-11-12 01:49:43.761669+00	2025-11-12 11:28:30.078471+00	9.65	41	2025-11-12 01:49:43.761669+00	182.3.104.27	\N	attendances/41/check_in/2025-11-12/7195ee10-4408-4f0a-8c7d-a703c4a66b16.jpeg	2025-11-12 11:28:30.078471+00	182.253.63.30	\N	attendances/41/check_out/2025-11-12/9682f57c-f89e-4940-8b89-f3c5f76cf107.jpeg	2025-11-12 01:49:44.91532+00	2025-11-12 11:28:30.819273+00	-5.04346990	104.30352770	Jalan Raya Bukit Kemuning - Liwa, Lampung Barat, Lampung, Sumatra, Indonesia	-5.38764260	105.28013950	Jalan Alam Kurnia, Kalibalau Kencana, Bandar Lampung, Lampung, Sumatra, 35133, Indonesia	\N
159	15	12	2025-11-12	present	2025-11-12 02:30:39.005036+00	2025-11-12 11:28:37.278724+00	8.97	15	2025-11-12 02:30:39.005036+00	182.3.100.198	\N	attendances/15/check_in/2025-11-12/addb49c1-a1ec-45e0-ba38-86c65e3066f8.jpeg	2025-11-12 11:28:37.278724+00	182.3.102.34	\N	attendances/15/check_out/2025-11-12/e66c2410-cd74-4f6a-9b43-a2080a3e6cf6.jpeg	2025-11-12 02:30:40.162853+00	2025-11-12 11:28:37.975522+00	-5.02822940	104.30405170	Jalan Raya Serengit, Mekar Sari, Lampung Barat, Lampung, Sumatra, Indonesia	-5.38757350	105.28013830	Jalan Alam Kurnia, Kalibalau Kencana, Bandar Lampung, Lampung, Sumatra, 35133, Indonesia	\N
924	51	23	2025-12-10	present	2025-12-10 07:24:12.110008+00	2025-12-10 10:14:06.178535+00	2.83	51	2025-12-10 07:24:12.110008+00	103.59.44.25	Gisting	attendances/51/check_in/2025-12-10/297d3ec9-4656-4204-af2a-5cf64bfcba95.jpeg	2025-12-10 10:14:06.178535+00	103.59.44.25	\N	attendances/51/check_out/2025-12-10/abd31739-efb7-45f7-aa49-a99e561ef9d9.jpeg	2025-12-10 07:24:13.012095+00	2025-12-10 10:14:07.168894+00	-5.43056250	104.73914980	Gisting Bawah, Tanggamus, Lampung, Sumatra, Indonesia	-5.43055170	104.73900000	Gisting Bawah, Tanggamus, Lampung, Sumatra, Indonesia	0.00
176	13	10	2025-11-12	absent	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	2025-11-12 16:00:01.696072+00	2025-11-12 16:00:01.696075+00	\N	\N	\N	\N	\N	\N	\N
185	14	11	2025-11-13	present	2025-11-13 02:11:46.993927+00	2025-11-13 11:18:11.313735+00	9.11	14	2025-11-13 02:11:46.993927+00	182.253.63.30	\N	attendances/14/check_in/2025-11-13/407ea919-61a7-435a-a611-027b86444557.jpeg	2025-11-13 11:18:11.313735+00	182.253.63.30	\N	attendances/14/check_out/2025-11-13/6038ced8-be89-4b46-8f1d-53776b49b3ea.jpeg	2025-11-13 02:11:47.73121+00	2025-11-13 11:18:12.625777+00	-5.37693280	105.27362020	Jalan Gunung Rajabasa Raya, Harapan Jaya, Bandar Lampung, Lampung, Sumatra, 35133, Indonesia	-5.37693280	105.27362020	Jalan Gunung Rajabasa Raya, Harapan Jaya, Bandar Lampung, Lampung, Sumatra, 35133, Indonesia	\N
187	24	15	2025-11-13	present	2025-11-13 02:23:47.421058+00	2025-11-13 12:30:52.292151+00	10.12	24	2025-11-13 02:23:47.421058+00	182.253.63.30	\N	attendances/24/check_in/2025-11-13/191b1aad-ce1e-4c3c-becb-a56e8a6d4df4.jpeg	2025-11-13 12:30:52.292151+00	182.253.63.30	\N	attendances/24/check_out/2025-11-13/d1522806-62d7-4a48-8029-6dfd9f9467bc.jpeg	2025-11-13 02:23:48.094157+00	2025-11-13 12:30:53.531068+00	-5.37693280	105.27362020	Jalan Gunung Rajabasa Raya, Harapan Jaya, Bandar Lampung, Lampung, Sumatra, 35133, Indonesia	-5.37694550	105.28166770	Harapan Jaya, Bandar Lampung, Lampung, Sumatra, 35133, Indonesia	\N
183	23	15	2025-11-13	present	2025-11-13 02:01:50.123499+00	2025-11-13 12:42:12.448074+00	10.67	23	2025-11-13 02:01:50.123499+00	182.253.63.30	\N	attendances/23/check_in/2025-11-13/834f2215-e980-4d78-bc57-b14e28e5e9b9.jpeg	2025-11-13 12:42:12.448074+00	182.253.63.30	\N	attendances/23/check_out/2025-11-13/de65c3aa-d7bd-480b-a48e-f3b6f14ec221.jpeg	2025-11-13 02:01:51.781707+00	2025-11-13 12:42:13.581375+00	-5.38756860	105.28017985	Jalan Alam Cantik, Kalibalau Kencana, Bandar Lampung, Lampung, Sumatra, 35133, Indonesia	-5.38759756	105.28021517	Jalan Alam Cantik, Kalibalau Kencana, Bandar Lampung, Lampung, Sumatra, 35133, Indonesia	\N
793	44	34	2025-12-06	present	2025-12-06 02:09:39.038576+00	2025-12-06 10:58:18.780062+00	8.81	44	2025-12-06 02:09:39.038576+00	114.10.100.137	\N	attendances/44/check_in/2025-12-06/6a359e8e-0917-402b-b59c-8e296a362554.jpeg	2025-12-06 10:58:18.780062+00	114.10.100.137	\N	attendances/44/check_out/2025-12-06/6871251b-1a5b-44c0-995f-d8e2326b97a1.jpeg	2025-12-06 02:09:40.67876+00	2025-12-06 10:58:20.323957+00	-5.36186170	105.24333000	Universitas Lampung UNILA, Jalan Jauhari Wahid, Labuhan Ratu, Bandar Lampung, Lampung, Sumatra, 35147, Indonesia	-5.37687020	105.25206300	Jalan Dakwah, Pelita, Bandar Lampung, Lampung, Sumatra, 35142, Indonesia	0.00
927	63	25	2025-12-10	present	2025-12-10 07:31:17.062024+00	2025-12-10 09:28:53.706913+00	1.96	63	2025-12-10 07:31:17.062024+00	103.87.231.107	\N	attendances/63/check_in/2025-12-10/d38fd95b-d981-4278-a2af-540d640b29d3.jpeg	2025-12-10 09:28:53.706913+00	103.87.231.107	\N	attendances/63/check_out/2025-12-10/31e48548-ae52-47db-943e-ac583d23b64e.jpeg	2025-12-10 07:31:17.948192+00	2025-12-10 09:28:54.748027+00	-5.02823340	104.30404670	Jalan Raya Serengit, Mekar Sari, Lampung Barat, Lampung, Sumatra, Indonesia	-5.02823100	104.30404690	Jalan Raya Serengit, Mekar Sari, Lampung Barat, Lampung, Sumatra, Indonesia	0.00
921	45	21	2025-12-10	present	2025-12-10 07:19:28.491779+00	2025-12-10 10:36:55.344803+00	3.29	45	2025-12-10 07:19:28.491779+00	103.144.14.2	\N	attendances/45/check_in/2025-12-10/1255f6d2-f4e5-41e3-85c8-d36f2cd34e3c.jpeg	2025-12-10 10:36:55.344803+00	114.125.252.211	\N	attendances/45/check_out/2025-12-10/1f1f4f98-6042-48a3-99e1-f136506702b1.jpeg	2025-12-10 07:19:29.290045+00	2025-12-10 10:36:56.050235+00	-4.05604730	103.29806680	Rantau Unji, Dempo Tengah, Pagar Alam, Sumatera Selatan, Sumatra, Indonesia	-4.05607350	103.29807040	Rantau Unji, Dempo Tengah, Pagar Alam, Sumatera Selatan, Sumatra, Indonesia	0.00
820	43	32	2025-12-06	absent	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	2025-12-06 16:00:00.415137+00	2025-12-06 16:00:00.415142+00	\N	\N	\N	\N	\N	\N	\N
931	64	24	2025-12-10	present	2025-12-10 07:34:05.644254+00	2025-12-10 13:11:50.643423+00	5.63	64	2025-12-10 07:34:05.644254+00	140.213.115.40	Mati lampu sabang sampai maroke	attendances/64/check_in/2025-12-10/fb73c954-7f68-4e76-a2fa-959be8e33906.jpeg	2025-12-10 13:11:50.643423+00	110.137.36.83	\N	attendances/64/check_out/2025-12-10/52180177-0bf6-49a7-93fb-6c42914df2a3.jpeg	2025-12-10 07:34:06.35623+00	2025-12-10 13:11:51.486906+00	-4.68575784	104.55329281	Tiuh Balak I, Way Kanan, Lampung, Sumatra, 34761, Indonesia	-4.85864785	104.93161454	Jalan Lintas Tengah Sumatera, Tanjung Harapan, Lampung Utara, Lampung, Sumatra, Indonesia	0.00
938	55	27	2025-12-10	absent	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	2025-12-10 16:00:00.142151+00	2025-12-10 16:00:00.142157+00	\N	\N	\N	\N	\N	\N	\N
1149	14	28	2025-12-17	present	2025-12-17 16:43:01.816005+00	2025-12-17 16:43:15.628387+00	0.00	\N	2025-12-17 16:43:01.816005+00	114.122.115.95	\N	attendances/14/check_in/2025-12-17/a7cf71f3-5a7a-40ba-bdab-6abd02aa85fe.jpeg	2025-12-17 16:43:15.628387+00	114.122.115.95	\N	attendances/14/check_out/2025-12-17/c9d8ca26-55e2-496c-ba49-d2d1f56b09b1.jpeg	2025-12-17 16:00:00.386034+00	2025-12-17 16:43:16.347058+00	-6.98573500	108.45028000	Cileuleuy, Kuningan, Jawa, 45563, Indonesia	-6.98573500	108.45028000	Cileuleuy, Kuningan, Jawa, 45563, Indonesia	0.00
846	42	28	2025-12-08	present	2025-12-08 02:09:07.035194+00	2025-12-08 10:30:37.916172+00	8.36	42	2025-12-08 02:09:07.035194+00	103.105.82.245	\N	attendances/42/check_in/2025-12-08/7c2cedd8-8972-4ba2-9c9b-f8bfcc7eb6a8.jpeg	2025-12-08 10:30:37.916172+00	103.105.82.245	\N	attendances/42/check_out/2025-12-08/49a7506c-144c-425c-93cf-bf5756cb32d4.jpeg	2025-12-08 02:09:07.824288+00	2025-12-08 10:30:39.081721+00	-5.38757500	105.28015840	Jalan Alam Cantik, Kalibalau Kencana, Bandar Lampung, Lampung, Sumatra, 35133, Indonesia	-5.38759120	105.28015700	Jalan Alam Kurnia, Kalibalau Kencana, Bandar Lampung, Lampung, Sumatra, 35133, Indonesia	0.00
849	41	21	2025-12-08	present	2025-12-08 02:36:31.591163+00	2025-12-08 10:48:50.32651+00	8.21	41	2025-12-08 02:36:31.591163+00	103.105.82.245	\N	attendances/41/check_in/2025-12-08/8a63955c-0993-4cfa-a3c2-34c46f8b0ad9.jpeg	2025-12-08 10:48:50.32651+00	103.105.82.245	\N	attendances/41/check_out/2025-12-08/647f0859-4c70-4b1b-a5cf-b4d4a22f1c60.jpeg	2025-12-08 02:36:32.587755+00	2025-12-08 10:48:51.477655+00	-5.38758394	105.28017986	Jalan Alam Cantik, Kalibalau Kencana, Bandar Lampung, Lampung, Sumatra, 35133, Indonesia	-5.38758394	105.28017986	Jalan Alam Cantik, Kalibalau Kencana, Bandar Lampung, Lampung, Sumatra, 35133, Indonesia	0.00
1153	58	27	2025-12-18	present	2025-12-18 01:02:08.360525+00	\N	\N	58	2025-12-18 01:02:08.360525+00	103.144.14.2	\N	attendances/58/check_in/2025-12-18/00db08ce-19f7-4e10-b13b-14f7d751e9c7.jpeg	\N	\N	\N	\N	2025-12-18 01:02:09.872646+00	2025-12-18 01:02:09.872651+00	-4.05567400	103.29738760	Rantau Unji, Dempo Tengah, Pagar Alam, Sumatera Selatan, Sumatra, Indonesia	\N	\N	\N	\N
942	64	24	2025-12-11	invalid	2025-12-10 23:26:52.071899+00	2025-12-11 16:39:02.967829+00	17.20	64	2025-12-10 23:26:52.071899+00	110.137.36.83	\N	attendances/64/check_in/2025-12-11/4fd464c9-1578-4c7a-b59d-a0819b66314d.jpeg	2025-12-11 16:39:02.967829+00	110.137.36.83	\N	attendances/64/check_out/2025-12-11/8bd8b21e-a89b-47e8-a440-6e366d420c21.jpeg	2025-12-10 23:26:53.532885+00	2025-12-11 16:39:04.27963+00	-4.85927062	104.93110968	Tanjung Harapan, Lampung Utara, Lampung, Sumatra, 34511, Indonesia	-4.85927062	104.93110968	Tanjung Harapan, Lampung Utara, Lampung, Sumatra, 34511, Indonesia	0.00
945	15	21	2025-12-11	invalid	2025-12-11 00:59:56.331129+00	2025-12-11 16:40:10.266561+00	15.67	15	2025-12-11 00:59:56.331129+00	103.144.14.2	\N	attendances/15/check_in/2025-12-11/95393403-847e-4ad5-8e3a-d6dfc38aa595.jpeg	2025-12-11 16:40:10.266561+00	103.144.14.2	\N	attendances/15/check_out/2025-12-11/20023cec-8544-412d-a420-50af0dac8bc4.jpeg	2025-12-11 00:59:57.375759+00	2025-12-11 16:40:10.994996+00	-4.05607160	103.29807100	Rantau Unji, Dempo Tengah, Pagar Alam, Sumatera Selatan, Sumatra, Indonesia	-4.01645280	103.24969840	Jalan Profesor Dokter Bakri Hamid, Pagar Alam Utara, Pagar Alam, Sumatera Selatan, Sumatra, Indonesia	0.00
1154	45	21	2025-12-18	present	2025-12-18 01:03:06.99117+00	\N	\N	45	2025-12-18 01:03:06.99117+00	114.125.247.118	\N	attendances/45/check_in/2025-12-18/680e4173-6b25-40bd-9039-e4416db69a14.jpeg	\N	\N	\N	\N	2025-12-18 01:03:07.871238+00	2025-12-18 01:03:07.871242+00	-4.05604299	103.29811906	Rantau Unji, Dempo Tengah, Pagar Alam, Sumatera Selatan, Sumatra, Indonesia	\N	\N	\N	\N
1156	24	31	2025-12-18	present	2025-12-18 01:26:59.104525+00	\N	\N	24	2025-12-18 01:26:59.104525+00	103.105.82.243	\N	attendances/24/check_in/2025-12-18/9b34c96f-166c-47fe-b9dd-981fdbe1f1fe.jpeg	\N	\N	\N	\N	2025-12-18 01:26:59.83306+00	2025-12-18 01:26:59.833064+00	-5.38758350	105.28016580	Jalan Alam Cantik, Kalibalau Kencana, Bandar Lampung, Lampung, Sumatra, 35133, Indonesia	\N	\N	\N	\N
1157	60	29	2025-12-18	present	2025-12-18 01:38:58.388713+00	\N	\N	60	2025-12-18 01:38:58.388713+00	103.145.34.18	\N	attendances/60/check_in/2025-12-18/be0d5052-36cb-4ed9-ac56-9885f7b4b7f7.jpeg	\N	\N	\N	\N	2025-12-18 01:38:59.495597+00	2025-12-18 01:38:59.495601+00	-5.42568880	104.73794490	Kota Dalam, Tanggamus, Lampung, Sumatra, Indonesia	\N	\N	\N	\N
1159	61	29	2025-12-18	present	2025-12-18 01:45:11.806309+00	\N	\N	61	2025-12-18 01:45:11.806309+00	114.10.100.146	Cuaca buruk	attendances/61/check_in/2025-12-18/d0862183-739e-411d-893f-a950beb42ee3.jpeg	\N	\N	\N	\N	2025-12-18 01:45:12.767951+00	2025-12-18 01:45:12.767956+00	-5.06713830	104.13013830	Lampung Barat, Lampung, Sumatra, Indonesia	\N	\N	\N	\N
190	44	17	2025-11-13	present	2025-11-13 02:52:53.963809+00	2025-11-13 11:10:51.278808+00	8.30	44	2025-11-13 02:52:53.963809+00	182.253.63.30	\N	attendances/44/check_in/2025-11-13/097aa4bd-ec86-4296-bf7d-2ca115b7c5c4.jpeg	2025-11-13 11:10:51.278808+00	114.10.100.162	\N	attendances/44/check_out/2025-11-13/e9b011b1-a911-45a8-8355-0dc9cd286c3b.jpeg	2025-11-13 02:52:54.962011+00	2025-11-13 11:10:52.852469+00	-5.38758180	105.28016510	Jalan Alam Cantik, Kalibalau Kencana, Bandar Lampung, Lampung, Sumatra, 35133, Indonesia	-5.38761510	105.28014490	Jalan Alam Kurnia, Kalibalau Kencana, Bandar Lampung, Lampung, Sumatra, 35133, Indonesia	\N
794	39	32	2025-12-06	present	2025-12-06 11:24:15.933241+00	2025-12-06 11:24:24.132273+00	0.00	39	2025-12-06 11:24:15.933241+00	114.10.100.161	\N	attendances/39/check_in/2025-12-06/b830ed01-a887-4a97-86ea-cb0c6d9c0b23.jpeg	2025-12-06 11:24:24.132273+00	114.10.100.161	\N	attendances/39/check_out/2025-12-06/fdfbdaae-3318-45c8-b88c-398cecdf5439.jpeg	2025-12-06 11:24:17.104936+00	2025-12-06 11:24:24.849314+00	-5.44117570	105.29602460	Jalan Perumahan Garuntang Lestari, Way Lunik, Bandar Lampung, Lampung, Sumatra, 35245, Indonesia	-5.44117570	105.29602460	Jalan Perumahan Garuntang Lestari, Way Lunik, Bandar Lampung, Lampung, Sumatra, 35245, Indonesia	0.00
797	23	33	2025-12-06	absent	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	2025-12-06 16:00:00.215847+00	2025-12-06 16:00:00.215852+00	\N	\N	\N	\N	\N	\N	\N
205	13	10	2025-11-13	absent	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	2025-11-13 16:00:00.262656+00	2025-11-13 16:00:00.262659+00	\N	\N	\N	\N	\N	\N	\N
211	39	17	2025-11-13	hybrid	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	2025-11-13 16:00:00.293229+00	2025-11-13 16:00:00.293233+00	\N	\N	\N	\N	\N	\N	\N
807	22	33	2025-12-06	absent	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	2025-12-06 16:00:00.322042+00	2025-12-06 16:00:00.322045+00	\N	\N	\N	\N	\N	\N	\N
922	57	27	2025-12-10	present	2025-12-10 07:20:53.076531+00	2025-12-10 07:28:22.227671+00	0.12	57	2025-12-10 07:20:53.076531+00	103.144.14.2	pagar alam	attendances/57/check_in/2025-12-10/18a91e3c-3848-4047-9af8-a1ec2d2ec7c4.jpeg	2025-12-10 07:28:22.227671+00	103.144.14.2	pagar alam	attendances/57/check_out/2025-12-10/9ccc11ab-d0e5-4b08-b722-ab83d3f7f3f8.jpeg	2025-12-10 07:20:54.019713+00	2025-12-10 07:28:22.997772+00	-4.05597426	103.29806414	Rantau Unji, Dempo Tengah, Pagar Alam, Sumatera Selatan, Sumatra, Indonesia	-4.05597426	103.29806414	Rantau Unji, Dempo Tengah, Pagar Alam, Sumatera Selatan, Sumatra, Indonesia	0.00
817	24	31	2025-12-06	absent	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	2025-12-06 16:00:00.390118+00	2025-12-06 16:00:00.390123+00	\N	\N	\N	\N	\N	\N	\N
822	41	21	2025-12-06	absent	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	2025-12-06 16:00:00.427998+00	2025-12-06 16:00:00.428004+00	\N	\N	\N	\N	\N	\N	\N
911	40	28	2025-12-10	present	2025-12-10 01:38:56.895744+00	2025-12-10 09:46:28.776359+00	8.13	40	2025-12-10 01:38:56.895744+00	103.105.82.245	\N	attendances/40/check_in/2025-12-10/15ae52c7-bdeb-4d38-ab67-4440089789e8.jpg	2025-12-10 09:46:28.776359+00	103.105.82.245	\N	attendances/40/check_out/2025-12-10/2a4a5c93-d461-4fda-b5b1-cf5864a33c25.jpg	2025-12-10 01:38:57.997713+00	2025-12-10 09:46:33.407116+00	-5.38070920	105.26996230	Perumnas Way Halim, Bandar Lampung, Lampung, Sumatra, 35132, Indonesia	-5.38070920	105.26996230	Perumnas Way Halim, Bandar Lampung, Lampung, Sumatra, 35132, Indonesia	0.00
935	46	21	2025-12-10	absent	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	2025-12-10 16:00:00.087181+00	2025-12-10 16:00:00.087188+00	\N	\N	\N	\N	\N	\N	\N
940	47	22	2025-12-10	absent	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	2025-12-10 16:00:00.166505+00	2025-12-10 16:00:00.16651+00	\N	\N	\N	\N	\N	\N	\N
1163	52	24	2025-12-18	present	2025-12-18 02:08:39.558063+00	\N	\N	52	2025-12-18 02:08:39.558063+00	114.10.100.79	Otw k bukit cek gudang	attendances/52/check_in/2025-12-18/a583057a-ddae-4974-9c89-7df3768356a0.jpeg	\N	\N	\N	\N	2025-12-18 02:08:40.573243+00	2025-12-18 02:08:40.573246+00	-5.05635560	104.31007930	Jalan Raya Bukit Kemuning - Liwa, Sekincau, Lampung Barat, Lampung, Sumatra, Indonesia	\N	\N	\N	\N
847	40	28	2025-12-08	present	2025-12-08 02:13:28.782706+00	2025-12-08 10:09:06.696131+00	7.93	40	2025-12-08 02:13:28.782706+00	103.105.82.245	\N	attendances/40/check_in/2025-12-08/758cb085-e3c8-4176-8de0-5b62a53c176b.jpeg	2025-12-08 10:09:06.696131+00	103.105.82.245	\N	attendances/40/check_out/2025-12-08/d69bd4a0-6608-49e1-aea3-8d867bec86f7.jpeg	2025-12-08 02:13:29.961541+00	2025-12-08 10:09:07.633255+00	-5.38762540	105.28014407	Jalan Alam Kurnia, Kalibalau Kencana, Bandar Lampung, Lampung, Sumatra, 35133, Indonesia	-5.38759397	105.28016704	Jalan Alam Kurnia, Kalibalau Kencana, Bandar Lampung, Lampung, Sumatra, 35133, Indonesia	0.00
845	24	31	2025-12-08	present	2025-12-08 02:04:30.323016+00	2025-12-08 10:50:55.380743+00	8.77	24	2025-12-08 02:04:30.323016+00	103.105.82.245	\N	attendances/24/check_in/2025-12-08/1847b354-eacf-4e4c-a0e6-c1d13a11b386.jpeg	2025-12-08 10:50:55.380743+00	114.10.100.177	\N	attendances/24/check_out/2025-12-08/ff2adb23-6e14-41f0-b211-90e51c5f20f8.jpeg	2025-12-08 02:04:31.900655+00	2025-12-08 10:50:56.125133+00	-5.38757820	105.28015520	Jalan Alam Cantik, Kalibalau Kencana, Bandar Lampung, Lampung, Sumatra, 35133, Indonesia	-5.38758190	105.28015220	Jalan Alam Kurnia, Kalibalau Kencana, Bandar Lampung, Lampung, Sumatra, 35133, Indonesia	0.00
851	22	33	2025-12-08	invalid	2025-12-08 03:19:29.071547+00	\N	\N	22	2025-12-08 03:19:29.071547+00	103.105.82.245	\N	attendances/22/check_in/2025-12-08/e150fd80-65e6-4563-a477-c88e1e25a7d7.jpeg	\N	\N	\N	\N	2025-12-08 03:19:30.313834+00	2025-12-08 16:30:00.041912+00	-5.37914640	105.29630060	Kalibalau Kencana, Bandar Lampung, Lampung, Sumatra, 35131, Indonesia	\N	\N	\N	\N
1172	15	21	2025-12-18	present	2025-12-18 03:01:21.361104+00	\N	\N	15	2025-12-18 03:01:21.361104+00	182.3.101.253	\N	attendances/15/check_in/2025-12-18/02c79392-2552-4fa3-89d4-d3f939f4d162.jpeg	\N	\N	\N	\N	2025-12-18 03:01:22.297055+00	2025-12-18 03:01:22.297059+00	-4.89754940	105.06508110	Jalan Lintas Tengah Sumatera, Banjar Kertarahayu, Lampung Tengah, Lampung, Sumatra, Indonesia	\N	\N	\N	\N
188	22	15	2025-11-13	present	2025-11-13 02:31:56.167717+00	2025-11-13 12:41:38.343703+00	10.16	22	2025-11-13 02:31:56.167717+00	182.253.63.30	\N	attendances/22/check_in/2025-11-13/7bb521a2-2545-4815-83ed-58098f1cd2a7.jpeg	2025-11-13 12:41:38.343703+00	182.253.63.30	\N	attendances/22/check_out/2025-11-13/4d5d15e2-56dc-4cc1-96e5-8d3897515371.jpeg	2025-11-13 02:31:57.264395+00	2025-11-13 12:41:41.654738+00	-5.37693280	105.27362020	Jalan Gunung Rajabasa Raya, Harapan Jaya, Bandar Lampung, Lampung, Sumatra, 35133, Indonesia	-5.37693280	105.27362020	Jalan Gunung Rajabasa Raya, Harapan Jaya, Bandar Lampung, Lampung, Sumatra, 35133, Indonesia	\N
795	40	28	2025-12-06	present	2025-12-06 12:18:19.886123+00	2025-12-06 12:18:30.132129+00	0.00	40	2025-12-06 12:18:19.886123+00	103.105.82.233	Gathering	attendances/40/check_in/2025-12-06/32d2baae-b77b-4e1a-acb3-4ed679a1a9a8.jpeg	2025-12-06 12:18:30.132129+00	103.105.82.233	Pulang gathering	attendances/40/check_out/2025-12-06/e3c93c6d-f11b-435c-8858-efd9e925df17.jpeg	2025-12-06 12:18:21.105865+00	2025-12-06 12:18:30.853425+00	-5.37932382	105.24537919	Jalan Bugenvil, Segala Mider, Bandar Lampung, Lampung, Sumatra, 35148, Indonesia	-5.37932382	105.24537919	Jalan Bugenvil, Segala Mider, Bandar Lampung, Lampung, Sumatra, 35148, Indonesia	0.00
923	59	29	2025-12-10	present	2025-12-10 07:22:13.485422+00	2025-12-10 07:23:04.700511+00	0.01	59	2025-12-10 07:22:13.485422+00	182.3.102.198	Perencanaan Tanam	attendances/59/check_in/2025-12-10/53bf31b9-835e-4a75-a24e-8b296841a532.jpg	2025-12-10 07:23:04.700511+00	182.3.102.198	\N	attendances/59/check_out/2025-12-10/b09b636e-fc82-4721-a041-d274fa31555d.jpeg	2025-12-10 07:22:14.334708+00	2025-12-10 07:23:05.54513+00	-5.37860170	105.21967900	RS Pertamina-Bintang Amin, 26, Jalan Pramuka, Kemiling Permai I, Bandar Lampung, Lampung, Sumatra, 35151, Indonesia	-5.37860170	105.21967900	RS Pertamina-Bintang Amin, 26, Jalan Pramuka, Kemiling Permai I, Bandar Lampung, Lampung, Sumatra, 35151, Indonesia	0.00
192	15	12	2025-11-13	invalid	2025-11-13 07:46:13.044195+00	\N	\N	15	2025-11-13 07:46:13.044195+00	182.253.63.30	\N	attendances/15/check_in/2025-11-13/d87b7ad4-1dff-4f80-95da-023a978a6968.jpeg	\N	\N	\N	\N	2025-11-13 07:46:14.864174+00	2025-11-13 16:59:00.058268+00	-5.38758050	105.28016380	Jalan Alam Cantik, Kalibalau Kencana, Bandar Lampung, Lampung, Sumatra, 35133, Indonesia	\N	\N	\N	\N
814	14	28	2025-12-06	absent	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	2025-12-06 16:00:00.370868+00	2025-12-06 16:00:00.370874+00	\N	\N	\N	\N	\N	\N	\N
819	20	31	2025-12-06	absent	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	2025-12-06 16:00:00.401502+00	2025-12-06 16:00:00.401508+00	\N	\N	\N	\N	\N	\N	\N
925	49	23	2025-12-10	present	2025-12-10 07:24:20.648128+00	2025-12-10 10:05:45.68098+00	2.69	49	2025-12-10 07:24:20.648128+00	103.59.44.25	Gisting	attendances/49/check_in/2025-12-10/42f8f4e4-f595-4df4-b0cc-a8f68d7016c7.jpeg	2025-12-10 10:05:45.68098+00	103.59.44.25	\N	attendances/49/check_out/2025-12-10/bb9a6ef8-49ac-49b4-b899-67bd23b40e2f.jpeg	2025-12-10 07:24:21.389156+00	2025-12-10 10:05:47.299101+00	-5.44144144	104.72417745	Gisting Atas, Tanggamus, Lampung, Sumatra, Indonesia	-5.42342342	104.72104560	Tanggamus, Lampung, Sumatra, Indonesia	0.00
934	60	29	2025-12-10	present	2025-12-10 13:17:35.61589+00	2025-12-10 13:17:57.49778+00	0.01	60	2025-12-10 13:17:35.61589+00	114.10.102.241	\N	attendances/60/check_in/2025-12-10/92c14e33-c5fa-4599-b56b-9aa4a91f61ff.jpeg	2025-12-10 13:17:57.49778+00	114.10.102.241	\N	attendances/60/check_out/2025-12-10/f0ce5b9b-e0f7-4662-b575-f683bdc78745.jpeg	2025-12-10 13:17:38.278961+00	2025-12-10 13:17:58.282122+00	-5.42570770	104.73796410	Kota Dalam, Tanggamus, Lampung, Sumatra, Indonesia	-5.42570770	104.73796410	Kota Dalam, Tanggamus, Lampung, Sumatra, Indonesia	0.00
936	54	25	2025-12-10	absent	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	2025-12-10 16:00:00.1155+00	2025-12-10 16:00:00.115504+00	\N	\N	\N	\N	\N	\N	\N
941	43	32	2025-12-10	hybrid	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	2025-12-10 16:00:00.178068+00	2025-12-10 16:00:00.178073+00	\N	\N	\N	\N	\N	\N	\N
850	44	34	2025-12-08	present	2025-12-08 02:46:35.408877+00	2025-12-08 11:52:39.326867+00	9.10	44	2025-12-08 02:46:35.408877+00	103.105.82.245	\N	attendances/44/check_in/2025-12-08/20a9aa16-6038-480b-b704-817b047381f6.jpeg	2025-12-08 11:52:39.326867+00	114.10.100.230	\N	attendances/44/check_out/2025-12-08/923dcd38-bb2a-4833-8d2b-5cbbc6d72a6f.jpeg	2025-12-08 02:46:36.618856+00	2025-12-08 11:52:41.331856+00	-5.38758430	105.28016020	Jalan Alam Cantik, Kalibalau Kencana, Bandar Lampung, Lampung, Sumatra, 35133, Indonesia	-5.38757980	105.28016270	Jalan Alam Cantik, Kalibalau Kencana, Bandar Lampung, Lampung, Sumatra, 35133, Indonesia	0.00
944	60	29	2025-12-11	present	2025-12-11 00:48:00.116743+00	2025-12-11 08:09:29.543866+00	7.36	60	2025-12-11 00:48:00.116743+00	103.145.34.18	\N	attendances/60/check_in/2025-12-11/25e83fff-9e1c-46f8-bad1-bc488c2d3138.jpeg	2025-12-11 08:09:29.543866+00	114.10.102.241	\N	attendances/60/check_out/2025-12-11/d4d8d8d0-acf7-4bd8-bac3-6edd3722889d.jpeg	2025-12-11 00:48:01.279232+00	2025-12-11 08:09:30.93341+00	-5.42570780	104.73796320	Kota Dalam, Tanggamus, Lampung, Sumatra, Indonesia	-5.43074760	104.73929430	Gisting Bawah, Tanggamus, Lampung, Sumatra, Indonesia	0.00
796	13	20	2025-12-06	absent	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	2025-12-06 16:00:00.159795+00	2025-12-06 16:00:00.159803+00	\N	\N	\N	\N	\N	\N	\N
161	20	14	2025-11-12	invalid	2025-11-12 03:20:53.931905+00	\N	\N	20	2025-11-12 03:20:53.931905+00	182.253.63.30	\N	attendances/20/check_in/2025-11-12/cabcd89d-a40b-4c4e-9a89-cdea942db090.jpeg	\N	\N	\N	\N	2025-11-12 03:20:55.276798+00	2025-11-12 16:59:00.047473+00	-5.36358130	105.28166770	Way Dadi, Bandar Lampung, Lampung, Sumatra, 35139, Indonesia	\N	\N	\N	\N
806	62	30	2025-12-06	absent	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	2025-12-06 16:00:00.31751+00	2025-12-06 16:00:00.317515+00	\N	\N	\N	\N	\N	\N	\N
821	42	28	2025-12-06	absent	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	2025-12-06 16:00:00.420478+00	2025-12-06 16:00:00.420483+00	\N	\N	\N	\N	\N	\N	\N
930	61	29	2025-12-10	present	2025-12-10 07:34:02.352916+00	2025-12-10 09:02:46.757983+00	1.48	61	2025-12-10 07:34:02.352916+00	114.10.102.38	\N	attendances/61/check_in/2025-12-10/8ee78a1a-2d12-4440-8628-3883c02396df.jpeg	2025-12-10 09:02:46.757983+00	114.10.102.38	\N	attendances/61/check_out/2025-12-10/aac67ed6-6e1d-4065-89c4-2fb28d9229e0.jpeg	2025-12-10 07:34:03.093467+00	2025-12-10 09:02:47.849465+00	-5.02981570	104.05183140	Lampung Barat, Lampung, Sumatra, 34812, Indonesia	-5.05138410	104.10752340	Gang Buntu, Liwa, Lampung Barat, Lampung, Sumatra, 34812, Indonesia	0.00
928	53	25	2025-12-10	present	2025-12-10 07:31:20.370561+00	2025-12-10 09:29:40.700087+00	1.97	53	2025-12-10 07:31:20.370561+00	103.87.231.107	\N	attendances/53/check_in/2025-12-10/29e9b66e-9f74-42b8-8c50-7f4ce3955873.jpeg	2025-12-10 09:29:40.700087+00	114.10.102.204	\N	attendances/53/check_out/2025-12-10/66294579-cf47-4272-bfb2-f8b8e7a78d73.jpeg	2025-12-10 07:31:21.137142+00	2025-12-10 09:29:41.463242+00	-5.02823240	104.30404710	Jalan Raya Serengit, Mekar Sari, Lampung Barat, Lampung, Sumatra, Indonesia	-5.02823340	104.30404670	Jalan Raya Serengit, Mekar Sari, Lampung Barat, Lampung, Sumatra, Indonesia	0.00
932	52	24	2025-12-10	present	2025-12-10 07:38:09.239057+00	2025-12-10 09:54:05.562714+00	2.27	52	2025-12-10 07:38:09.239057+00	114.10.100.18	\N	attendances/52/check_in/2025-12-10/9f2ce1a1-bc73-4587-8075-3e4faf6d01b3.jpeg	2025-12-10 09:54:05.562714+00	114.10.100.18	\N	attendances/52/check_out/2025-12-10/99167c44-3ab2-45e2-8d65-66c5611550cf.jpeg	2025-12-10 07:38:10.288012+00	2025-12-10 09:54:06.56046+00	-5.03032020	104.07373000	Liwa, Lampung Barat, Lampung, Sumatra, 34812, Indonesia	-5.03574280	104.30235480	Jalan Raya Bukit Kemuning - Liwa, Lampung Barat, Lampung, Sumatra, Indonesia	0.00
937	62	30	2025-12-10	absent	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	2025-12-10 16:00:00.122713+00	2025-12-10 16:00:00.122718+00	\N	\N	\N	\N	\N	\N	\N
943	61	29	2025-12-11	present	2025-12-10 23:49:26.102158+00	2025-12-11 10:36:24.290074+00	10.78	61	2025-12-10 23:49:26.102158+00	114.10.102.95	\N	attendances/61/check_in/2025-12-11/d418cb4d-a4e8-4828-9d9d-20405dacdc60.jpeg	2025-12-11 10:36:24.290074+00	114.10.102.95	Selesai bongkar kohe lokasi manabar atas	attendances/61/check_out/2025-12-11/079b2038-a743-41c8-9333-1edb014cc318.jpeg	2025-12-10 23:49:27.112802+00	2025-12-11 10:36:25.363112+00	-5.05154450	104.10748630	Gang Buntu, Liwa, Lampung Barat, Lampung, Sumatra, 34812, Indonesia	-5.06657170	104.13467980	Lampung Barat, Lampung, Sumatra, Indonesia	0.00
186	40	11	2025-11-13	present	2025-11-13 02:22:40.6213+00	2025-11-13 10:29:09.731218+00	8.11	40	2025-11-13 02:22:40.6213+00	182.253.63.30	\N	attendances/40/check_in/2025-11-13/fbd5a7d9-9c42-4168-8d38-4d4c26000b19.jpeg	2025-11-13 10:29:09.731218+00	182.253.63.30	\N	attendances/40/check_out/2025-11-13/b2599dd6-c34b-4fe7-b3c4-e417466c6180.jpeg	2025-11-13 02:22:41.811752+00	2025-11-13 10:29:10.879425+00	-5.37693280	105.27362020	Jalan Gunung Rajabasa Raya, Harapan Jaya, Bandar Lampung, Lampung, Sumatra, 35133, Indonesia	-5.38758326	105.28016838	Jalan Alam Cantik, Kalibalau Kencana, Bandar Lampung, Lampung, Sumatra, 35133, Indonesia	\N
929	39	32	2025-12-10	present	2025-12-10 07:33:59.580892+00	2025-12-10 08:23:51.299067+00	0.83	39	2025-12-10 07:33:59.580892+00	103.105.82.245	\N	attendances/39/check_in/2025-12-10/2e121e72-5089-4999-a1d4-2a9348cbbf0f.jpeg	2025-12-10 08:23:51.299067+00	103.105.82.245	\N	attendances/39/check_out/2025-12-10/d4a427dd-aca0-4b77-aed0-f3e0ba6f52f8.jpeg	2025-12-10 07:34:00.361874+00	2025-12-10 08:23:52.347089+00	-5.38758640	105.28015960	Jalan Alam Kurnia, Kalibalau Kencana, Bandar Lampung, Lampung, Sumatra, 35133, Indonesia	-5.38758060	105.28014690	Jalan Alam Kurnia, Kalibalau Kencana, Bandar Lampung, Lampung, Sumatra, 35133, Indonesia	0.00
926	48	23	2025-12-10	present	2025-12-10 07:27:48.98568+00	2025-12-10 09:03:44.061189+00	1.60	48	2025-12-10 07:27:48.98568+00	103.59.44.25	Gudang Gisting 	attendances/48/check_in/2025-12-10/eee22804-faa8-4eae-81a6-e3971af2d6d8.jpeg	2025-12-10 09:03:44.061189+00	103.59.44.25	Mau antar istri berobat 	attendances/48/check_out/2025-12-10/f33b8250-fd31-46e3-9aa1-7ff9bfe6f2a3.jpeg	2025-12-10 07:27:49.682483+00	2025-12-10 09:03:45.654704+00	-5.43064830	104.73900000	Gisting Bawah, Tanggamus, Lampung, Sumatra, Indonesia	-5.43011500	104.73877830	Gisting Bawah, Tanggamus, Lampung, Sumatra, Indonesia	0.00
212	43	17	2025-11-13	hybrid	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	2025-11-13 16:00:00.299017+00	2025-11-13 16:00:00.29902+00	\N	\N	\N	\N	\N	\N	\N
933	50	23	2025-12-10	present	2025-12-10 07:40:23.374962+00	2025-12-10 11:27:56.135536+00	3.79	50	2025-12-10 07:40:23.374962+00	114.10.102.157	\N	attendances/50/check_in/2025-12-10/4c801e1e-3a80-4b22-ad1c-b19d5dea9bb2.jpeg	2025-12-10 11:27:56.135536+00	114.10.102.157	\N	attendances/50/check_out/2025-12-10/5a0f2cee-6759-47af-be3b-f2f243603ef2.jpeg	2025-12-10 07:40:24.11077+00	2025-12-10 11:27:57.122981+00	-5.42933310	104.73404680	Gisting Bawah, Tanggamus, Lampung, Sumatra, Indonesia	-5.42973140	104.73419610	Gisting Bawah, Tanggamus, Lampung, Sumatra, Indonesia	0.00
823	15	21	2025-12-06	absent	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	2025-12-06 16:00:00.434907+00	2025-12-06 16:00:00.43493+00	\N	\N	\N	\N	\N	\N	\N
939	58	27	2025-12-10	absent	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	2025-12-10 16:00:00.153494+00	2025-12-10 16:00:00.153499+00	\N	\N	\N	\N	\N	\N	\N
848	23	33	2025-12-08	present	2025-12-08 02:13:41.34843+00	2025-12-08 15:53:04.69512+00	13.66	23	2025-12-08 02:13:41.34843+00	140.213.156.13	\N	attendances/23/check_in/2025-12-08/cc7bcffc-cab1-41a0-8892-de5dee45c5a7.jpeg	2025-12-08 15:53:04.69512+00	140.213.156.41	\N	attendances/23/check_out/2025-12-08/5d1bb4ba-042e-44f1-b336-3561e1beff4c.jpeg	2025-12-08 02:13:42.181023+00	2025-12-08 15:53:06.514411+00	-5.38754030	105.28024723	Jalan Alam Cantik, Kalibalau Kencana, Bandar Lampung, Lampung, Sumatra, 35133, Indonesia	-5.39003077	105.27922374	Kalibalau Kencana, Bandar Lampung, Lampung, Sumatra, 35133, Indonesia	0.00
182	43	17	2025-11-12	hybrid	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	2025-11-12 16:00:02.400705+00	2025-11-12 16:00:02.400712+00	\N	\N	\N	\N	\N	\N	\N
184	42	11	2025-11-13	present	2025-11-13 02:11:12.531157+00	2025-11-13 10:13:38.780564+00	8.04	42	2025-11-13 02:11:12.531157+00	182.3.102.67	\N	attendances/42/check_in/2025-11-13/a867dcea-e502-4a34-a1ec-671006d23d05.jpeg	2025-11-13 10:13:38.780564+00	182.253.63.30	\N	attendances/42/check_out/2025-11-13/23fe51f6-fa52-4ca3-ab58-120629f59c45.jpeg	2025-11-13 02:11:13.613621+00	2025-11-13 10:13:40.369998+00	-5.38757900	105.28015690	Jalan Alam Cantik, Kalibalau Kencana, Bandar Lampung, Lampung, Sumatra, 35133, Indonesia	-5.38757750	105.28015090	Jalan Alam Kurnia, Kalibalau Kencana, Bandar Lampung, Lampung, Sumatra, 35133, Indonesia	\N
189	41	12	2025-11-13	present	2025-11-13 02:33:56.633932+00	2025-11-13 10:14:40.254622+00	7.68	41	2025-11-13 02:33:56.633932+00	182.253.63.30	\N	attendances/41/check_in/2025-11-13/06f10489-1db7-43d0-b1e5-83a1a3ebf33c.jpeg	2025-11-13 10:14:40.254622+00	182.253.63.30	\N	attendances/41/check_out/2025-11-13/7b752dbd-e4c1-4b1d-8156-1b140fe724da.jpeg	2025-11-13 02:33:57.351042+00	2025-11-13 10:14:41.123094+00	-5.38758420	105.28016170	Jalan Alam Cantik, Kalibalau Kencana, Bandar Lampung, Lampung, Sumatra, 35133, Indonesia	-5.38759040	105.28015720	Jalan Alam Kurnia, Kalibalau Kencana, Bandar Lampung, Lampung, Sumatra, 35133, Indonesia	\N
191	20	14	2025-11-13	present	2025-11-13 03:54:02.444369+00	2025-11-13 12:10:40.52425+00	8.28	20	2025-11-13 03:54:02.444369+00	182.253.63.30	\N	attendances/20/check_in/2025-11-13/b64aed7e-1b17-45bf-85b0-495b6c3d686d.jpeg	2025-11-13 12:10:40.52425+00	182.253.63.30	\N	attendances/20/check_out/2025-11-13/c1a6afbf-4ec1-426c-bb66-a79fe5e3af1e.jpeg	2025-11-13 03:54:03.585763+00	2025-11-13 12:10:41.718145+00	-5.37693280	105.27362020	Jalan Gunung Rajabasa Raya, Harapan Jaya, Bandar Lampung, Lampung, Sumatra, 35133, Indonesia	-5.37694550	105.28166770	Harapan Jaya, Bandar Lampung, Lampung, Sumatra, 35133, Indonesia	\N
852	15	21	2025-12-08	invalid	2025-12-08 08:37:17.212543+00	\N	\N	15	2025-12-08 08:37:17.212543+00	103.105.82.245	Lupa check in	attendances/15/check_in/2025-12-08/fd054484-20bf-4e6b-b8a5-ef5273ef5999.jpeg	\N	\N	\N	\N	2025-12-08 08:37:18.736186+00	2025-12-08 16:30:00.047989+00	-5.38758320	105.28015860	Jalan Alam Cantik, Kalibalau Kencana, Bandar Lampung, Lampung, Sumatra, 35133, Indonesia	\N	\N	\N	\N
946	45	21	2025-12-11	present	2025-12-11 01:07:10.4181+00	2025-12-11 10:26:47.497462+00	9.33	45	2025-12-11 01:07:10.4181+00	103.144.14.2	\N	attendances/45/check_in/2025-12-11/04ec8406-7e3b-4db0-9042-0d10236643d5.jpeg	2025-12-11 10:26:47.497462+00	103.144.14.2	\N	attendances/45/check_out/2025-12-11/37aabea5-a161-493a-bf04-8868d984b548.jpeg	2025-12-11 01:07:11.562662+00	2025-12-11 10:26:48.473749+00	-4.05607160	103.29806980	Rantau Unji, Dempo Tengah, Pagar Alam, Sumatera Selatan, Sumatra, Indonesia	-4.05603230	103.29810899	Rantau Unji, Dempo Tengah, Pagar Alam, Sumatera Selatan, Sumatra, Indonesia	0.00
213	40	11	2025-11-14	present	2025-11-14 02:15:24.099343+00	2025-11-14 10:00:21.061899+00	7.75	40	2025-11-14 02:15:24.099343+00	182.253.63.30	\N	attendances/40/check_in/2025-11-14/9c6cce11-ebbd-4c52-a3e8-d08843c43e20.jpeg	2025-11-14 10:00:21.061899+00	182.253.63.30	\N	attendances/40/check_out/2025-11-14/66f09bdd-4d64-4fd4-be5c-f41f0824245d.jpeg	2025-11-14 02:15:25.801052+00	2025-11-14 10:00:23.375297+00	-5.37694550	105.28166770	Harapan Jaya, Bandar Lampung, Lampung, Sumatra, 35133, Indonesia	-5.37693970	105.27800970	Nasi Uduk Tante, Perumnas Way Halim, Harapan Jaya, Bandar Lampung, Lampung, Sumatra, 35133, Indonesia	\N
220	42	11	2025-11-14	present	2025-11-14 03:11:11.923469+00	2025-11-14 10:07:00.686885+00	6.93	42	2025-11-14 03:11:11.923469+00	182.253.63.30	\N	attendances/42/check_in/2025-11-14/d6caa696-58e9-4d39-96c0-6d210f29e6b6.jpeg	2025-11-14 10:07:00.686885+00	182.253.63.30	\N	attendances/42/check_out/2025-11-14/5c65fbc7-204f-4df1-bdf6-22caf12142a6.jpeg	2025-11-14 03:11:12.680316+00	2025-11-14 10:07:01.608342+00	-5.38758150	105.28016480	Jalan Alam Cantik, Kalibalau Kencana, Bandar Lampung, Lampung, Sumatra, 35133, Indonesia	-5.38765580	105.28013520	Jalan Alam Kurnia, Kalibalau Kencana, Bandar Lampung, Lampung, Sumatra, 35133, Indonesia	\N
221	39	17	2025-11-14	present	2025-11-14 03:11:18.449239+00	2025-11-14 10:10:51.331069+00	6.99	39	2025-11-14 03:11:18.449239+00	182.253.63.30	\N	attendances/39/check_in/2025-11-14/5547e8d8-0f28-4156-aba6-c829bd00dfc9.jpeg	2025-11-14 10:10:51.331069+00	182.253.63.30	\N	attendances/39/check_out/2025-11-14/b92effc3-b2ea-4de6-a7f6-46030b14239a.jpeg	2025-11-14 03:11:19.165316+00	2025-11-14 10:10:51.992939+00	-5.38758040	105.28016440	Jalan Alam Cantik, Kalibalau Kencana, Bandar Lampung, Lampung, Sumatra, 35133, Indonesia	-5.38765440	105.28013390	Jalan Alam Kurnia, Kalibalau Kencana, Bandar Lampung, Lampung, Sumatra, 35133, Indonesia	\N
217	24	15	2025-11-14	present	2025-11-14 02:57:12.778982+00	2025-11-14 10:27:37.043691+00	7.51	24	2025-11-14 02:57:12.778982+00	182.253.63.30	\N	attendances/24/check_in/2025-11-14/46e62afe-3b09-4178-9e34-63ea2f8cc3a5.jpeg	2025-11-14 10:27:37.043691+00	182.253.63.30	\N	attendances/24/check_out/2025-11-14/ad7a4fc6-f849-40cb-8054-3d7e25259b0d.jpeg	2025-11-14 02:57:13.686288+00	2025-11-14 10:27:38.107725+00	-5.37694550	105.28166770	Harapan Jaya, Bandar Lampung, Lampung, Sumatra, 35133, Indonesia	-5.37694550	105.28166770	Harapan Jaya, Bandar Lampung, Lampung, Sumatra, 35133, Indonesia	\N
222	44	17	2025-11-14	present	2025-11-14 03:21:51.872179+00	2025-11-14 10:37:11.834554+00	7.26	44	2025-11-14 03:21:51.872179+00	182.253.63.30	\N	attendances/44/check_in/2025-11-14/3182816f-560c-4877-9273-f499d233296d.jpeg	2025-11-14 10:37:11.834554+00	182.253.63.30	\N	attendances/44/check_out/2025-11-14/e4899aeb-49c3-4cf3-9194-bb39aec06b92.jpeg	2025-11-14 03:21:53.066037+00	2025-11-14 10:37:13.007926+00	-5.38758930	105.28016130	Jalan Alam Kurnia, Kalibalau Kencana, Bandar Lampung, Lampung, Sumatra, 35133, Indonesia	-5.38758990	105.28015820	Jalan Alam Kurnia, Kalibalau Kencana, Bandar Lampung, Lampung, Sumatra, 35133, Indonesia	\N
215	23	15	2025-11-14	present	2025-11-14 02:38:46.711912+00	2025-11-14 10:41:16.760057+00	8.04	23	2025-11-14 02:38:46.711912+00	182.253.63.30	\N	attendances/23/check_in/2025-11-14/effa771e-a017-4bee-84b5-b27a3fe6f6b1.jpeg	2025-11-14 10:41:16.760057+00	140.213.114.198	\N	attendances/23/check_out/2025-11-14/a7290443-0406-4f90-83a2-2febbe27c880.jpeg	2025-11-14 02:38:47.515072+00	2025-11-14 10:41:17.664465+00	-5.38753705	105.28018177	Jalan Alam Cantik, Kalibalau Kencana, Bandar Lampung, Lampung, Sumatra, 35133, Indonesia	-5.38755117	105.28014461	Jalan Alam Cantik, Kalibalau Kencana, Bandar Lampung, Lampung, Sumatra, 35133, Indonesia	\N
214	20	14	2025-11-14	present	2025-11-14 02:36:54.703313+00	2025-11-14 10:57:28.255368+00	8.34	20	2025-11-14 02:36:54.703313+00	182.253.63.30	\N	attendances/20/check_in/2025-11-14/e2a8725b-89b6-49a5-9901-e98bee7f7fea.jpeg	2025-11-14 10:57:28.255368+00	182.253.63.30	\N	attendances/20/check_out/2025-11-14/d40befe6-1fe9-493f-81b6-687ff515b839.jpeg	2025-11-14 02:36:55.822099+00	2025-11-14 10:57:28.588868+00	-5.37694550	105.28166770	Harapan Jaya, Bandar Lampung, Lampung, Sumatra, 35133, Indonesia	\N	\N	\N	\N
959	14	28	2025-12-11	present	2025-12-11 02:21:46.372317+00	2025-12-11 10:49:31.867917+00	8.46	14	2025-12-11 02:21:46.372317+00	103.105.82.245	\N	attendances/14/check_in/2025-12-11/8fe6764e-9732-4d49-a5b2-34254043247c.jpeg	2025-12-11 10:49:31.867917+00	103.105.82.245	\N	attendances/14/check_out/2025-12-11/a21af9f4-3bdf-45ba-8be7-25932d2084fe.jpeg	2025-12-11 02:21:47.043071+00	2025-12-11 10:49:34.321995+00	-5.39283020	105.26996230	Jagabaya II, Bandar Lampung, Lampung, Sumatra, 35136, Indonesia	-5.39283020	105.26996230	Jagabaya II, Bandar Lampung, Lampung, Sumatra, 35136, Indonesia	0.00
236	13	10	2025-11-14	absent	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	2025-11-14 16:00:00.773345+00	2025-11-14 16:00:00.773348+00	\N	\N	\N	\N	\N	\N	\N
242	43	17	2025-11-14	hybrid	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	2025-11-14 16:00:00.803495+00	2025-11-14 16:00:00.803499+00	\N	\N	\N	\N	\N	\N	\N
249	41	12	2025-11-15	present	2025-11-15 03:09:42.66998+00	2025-11-15 07:13:27.894374+00	4.06	41	2025-11-15 03:09:42.66998+00	182.253.63.30	\N	attendances/41/check_in/2025-11-15/99ad66b3-8a01-43a8-83b4-141762551aed.jpeg	2025-11-15 07:13:27.894374+00	182.253.63.30	\N	attendances/41/check_out/2025-11-15/aa7021bd-86c3-4705-94ff-da65bc43e111.jpeg	2025-11-15 03:09:43.981048+00	2025-11-15 07:13:28.681172+00	-5.37693970	105.27800970	Nasi Uduk Tante, Perumnas Way Halim, Harapan Jaya, Bandar Lampung, Lampung, Sumatra, 35133, Indonesia	-5.38758040	105.28016410	Jalan Alam Cantik, Kalibalau Kencana, Bandar Lampung, Lampung, Sumatra, 35133, Indonesia	\N
301	39	17	2025-11-17	hybrid	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	2025-11-17 16:00:00.518153+00	2025-11-17 16:00:00.518157+00	\N	\N	\N	\N	\N	\N	\N
302	43	17	2025-11-17	hybrid	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	2025-11-17 16:00:00.525079+00	2025-11-17 16:00:00.525083+00	\N	\N	\N	\N	\N	\N	\N
216	22	15	2025-11-14	invalid	2025-11-14 02:56:35.783098+00	\N	\N	22	2025-11-14 02:56:35.783098+00	182.253.63.30	\N	attendances/22/check_in/2025-11-14/26553b01-f917-4270-a3f6-1e426fadf8b3.jpeg	\N	\N	\N	\N	2025-11-14 02:56:35.94602+00	2025-11-14 16:59:00.038531+00	\N	\N	\N	\N	\N	\N	\N
218	15	12	2025-11-14	invalid	2025-11-14 03:01:21.503692+00	\N	\N	15	2025-11-14 03:01:21.503692+00	182.3.100.142	\N	attendances/15/check_in/2025-11-14/11f69745-7b9e-4db4-9b68-15cb1414e9d4.jpeg	\N	\N	\N	\N	2025-11-14 03:01:22.330325+00	2025-11-14 16:59:00.045748+00	-5.38758050	105.28016380	Jalan Alam Cantik, Kalibalau Kencana, Bandar Lampung, Lampung, Sumatra, 35133, Indonesia	\N	\N	\N	\N
219	14	11	2025-11-14	invalid	2025-11-14 03:10:57.096915+00	\N	\N	14	2025-11-14 03:10:57.096915+00	182.253.63.30	\N	attendances/14/check_in/2025-11-14/714f6a2e-b533-4752-a174-43ee98a887be.jpeg	\N	\N	\N	\N	2025-11-14 03:10:58.133573+00	2025-11-14 16:59:00.04689+00	-5.37693280	105.27362020	Jalan Gunung Rajabasa Raya, Harapan Jaya, Bandar Lampung, Lampung, Sumatra, 35133, Indonesia	\N	\N	\N	\N
223	41	12	2025-11-14	invalid	2025-11-14 03:30:11.611199+00	\N	\N	41	2025-11-14 03:30:11.611199+00	182.253.63.30	\N	attendances/41/check_in/2025-11-14/2a14d5a0-6b0f-43a0-9427-b79bbd624315.jpeg	\N	\N	\N	\N	2025-11-14 03:30:12.676713+00	2025-11-14 16:59:00.047923+00	-5.38758600	105.28015870	Jalan Alam Kurnia, Kalibalau Kencana, Bandar Lampung, Lampung, Sumatra, 35133, Indonesia	\N	\N	\N	\N
246	24	15	2025-11-15	present	2025-11-15 02:44:39.189143+00	2025-11-15 06:49:04.527007+00	4.07	24	2025-11-15 02:44:39.189143+00	182.253.63.30	\N	attendances/24/check_in/2025-11-15/427e81c3-a346-4c12-a7cf-d332b4ea63e7.jpeg	2025-11-15 06:49:04.527007+00	182.253.63.30	\N	attendances/24/check_out/2025-11-15/879c5387-7992-4c9c-a72d-b3a6afff275e.jpeg	2025-11-15 02:44:40.243111+00	2025-11-15 06:49:06.076835+00	-5.37693970	105.27800970	Nasi Uduk Tante, Perumnas Way Halim, Harapan Jaya, Bandar Lampung, Lampung, Sumatra, 35133, Indonesia	-5.37943480	105.27800970	Stadion Way Halim, Way Halim Permai, Bandar Lampung, Lampung, Sumatra, 35133, Indonesia	\N
243	40	11	2025-11-15	present	2025-11-15 02:12:52.505133+00	2025-11-15 07:46:53.425674+00	5.57	40	2025-11-15 02:12:52.505133+00	182.253.63.30	\N	attendances/40/check_in/2025-11-15/723ab959-40f8-4e5f-868e-2fc10ec58aa4.jpeg	2025-11-15 07:46:53.425674+00	182.253.63.30	\N	attendances/40/check_out/2025-11-15/9a554d78-df6a-470f-bc1b-a88991733252.jpeg	2025-11-15 02:12:53.896117+00	2025-11-15 07:46:54.406965+00	-5.37693970	105.27800970	Nasi Uduk Tante, Perumnas Way Halim, Harapan Jaya, Bandar Lampung, Lampung, Sumatra, 35133, Indonesia	-5.37943480	105.27800970	Stadion Way Halim, Harapan Jaya, Bandar Lampung, Lampung, Sumatra, 35133, Indonesia	\N
248	44	17	2025-11-15	present	2025-11-15 03:01:53.79026+00	2025-11-15 10:23:13.500678+00	7.36	44	2025-11-15 03:01:53.79026+00	114.10.102.86	\N	attendances/44/check_in/2025-11-15/72510df6-cf00-42d9-8ed0-c8c8be0151d2.jpeg	2025-11-15 10:23:13.500678+00	114.10.102.86	\N	attendances/44/check_out/2025-11-15/a204a3ab-ca35-4e3a-b714-c4033b703f5c.jpeg	2025-11-15 03:01:54.855724+00	2025-11-15 10:23:14.690408+00	-5.36167850	105.24346040	Fakultas Ekonomi dan Bisnis Universitas Lampung, Gang M. Said, Sepang Jaya, Bandar Lampung, Lampung, Sumatra, 35141, Indonesia	-5.37265830	105.24939830	Gang Zakaria III, Sepang Jaya, Bandar Lampung, Lampung, Sumatra, 35148, Indonesia	\N
853	14	28	2025-12-08	present	2025-12-08 10:06:57.653087+00	2025-12-08 10:07:11.579256+00	0.00	14	2025-12-08 10:06:57.653087+00	103.105.82.245	\N	attendances/14/check_in/2025-12-08/ab7d6bf9-cf2a-467b-9f05-fc27733802db.jpeg	2025-12-08 10:07:11.579256+00	103.105.82.245	\N	attendances/14/check_out/2025-12-08/6b82baa2-1f8d-4532-9538-16009e589316.jpeg	2025-12-08 10:06:59.304991+00	2025-12-08 10:07:12.43126+00	-5.37943930	105.28093610	Stadion Way Halim, Harapan Jaya, Bandar Lampung, Lampung, Sumatra, 35133, Indonesia	-5.37943930	105.28093610	Stadion Way Halim, Harapan Jaya, Bandar Lampung, Lampung, Sumatra, 35133, Indonesia	0.00
962	41	21	2025-12-11	present	2025-12-11 02:41:14.784115+00	2025-12-11 10:00:34.483308+00	7.32	41	2025-12-11 02:41:14.784115+00	103.105.82.245	\N	attendances/41/check_in/2025-12-11/94b389c4-10de-4adc-8f10-12a90f9be8c6.jpeg	2025-12-11 10:00:34.483308+00	103.105.82.245	\N	attendances/41/check_out/2025-12-11/df29d83e-98e4-4e67-943f-e6a833940708.jpeg	2025-12-11 02:41:15.636219+00	2025-12-11 10:00:35.984065+00	-5.38749886	105.28020839	Jalan Alam Cantik, Kalibalau Kencana, Bandar Lampung, Lampung, Sumatra, 35133, Indonesia	-5.38757454	105.28018294	Jalan Alam Cantik, Kalibalau Kencana, Bandar Lampung, Lampung, Sumatra, 35133, Indonesia	0.00
955	48	23	2025-12-11	present	2025-12-11 02:10:57.358571+00	2025-12-11 10:12:17.229971+00	8.02	48	2025-12-11 02:10:57.358571+00	103.59.44.25	\N	attendances/48/check_in/2025-12-11/b65278bf-cc2f-4604-ac2b-831214b0450c.jpeg	2025-12-11 10:12:17.229971+00	103.59.44.25	\N	attendances/48/check_out/2025-12-11/93c2b391-a306-462c-a9bd-4ab3ba711943.jpeg	2025-12-11 02:10:58.148593+00	2025-12-11 10:12:18.250943+00	-5.43064500	104.73903170	Gisting Bawah, Tanggamus, Lampung, Sumatra, Indonesia	-5.43063500	104.73898510	Gisting Bawah, Tanggamus, Lampung, Sumatra, Indonesia	0.00
947	49	23	2025-12-11	present	2025-12-11 01:20:20.221802+00	2025-12-11 10:18:40.530687+00	8.97	49	2025-12-11 01:20:20.221802+00	103.59.44.25	\N	attendances/49/check_in/2025-12-11/1640f67c-9ae4-4b14-9aab-1f17a42390b8.jpeg	2025-12-11 10:18:40.530687+00	103.59.44.25	\N	attendances/49/check_out/2025-12-11/be451ffb-e184-4b6c-8481-d93e0c329386.jpeg	2025-12-11 01:20:20.987187+00	2025-12-11 10:18:41.260053+00	-5.43060650	104.73910560	Gisting Bawah, Tanggamus, Lampung, Sumatra, Indonesia	-5.43058570	104.73918050	Gisting Bawah, Tanggamus, Lampung, Sumatra, Indonesia	0.00
961	22	33	2025-12-11	present	2025-12-11 02:40:30.005117+00	2025-12-11 10:48:59.05386+00	8.14	22	2025-12-11 02:40:30.005117+00	103.105.82.245	\N	attendances/22/check_in/2025-12-11/34124760-1f17-4b25-8605-b6b45214ba26.jpeg	2025-12-11 10:48:59.05386+00	103.105.82.245	\N	attendances/22/check_out/2025-12-11/8e1fa4e9-fe41-406e-a329-613e2078dcc7.jpeg	2025-12-11 02:40:30.846672+00	2025-12-11 10:49:00.379537+00	-5.39283020	105.26996230	Jagabaya II, Bandar Lampung, Lampung, Sumatra, 35136, Indonesia	-5.39620980	105.27800970	Jalan Pulau Morotai, Tanjung Baru, Bandar Lampung, Lampung, Sumatra, 35227, Indonesia	0.00
953	53	25	2025-12-11	present	2025-12-11 01:57:27.278998+00	2025-12-11 14:03:00.032249+00	12.09	53	2025-12-11 01:57:27.278998+00	114.10.100.2	\N	attendances/53/check_in/2025-12-11/0a1eccf2-6ce5-4809-9d74-ed4f3ac06c59.jpeg	2025-12-11 14:03:00.032249+00	114.10.100.68	\N	attendances/53/check_out/2025-12-11/b7e92174-a9aa-4b07-96a3-e0b5b1a94350.jpeg	2025-12-11 01:57:28.026489+00	2025-12-11 14:03:03.708119+00	-5.02818940	104.30404660	Jalan Raya Serengit, Mekar Sari, Lampung Barat, Lampung, Sumatra, Indonesia	-5.02822520	104.30405660	Jalan Raya Serengit, Mekar Sari, Lampung Barat, Lampung, Sumatra, Indonesia	0.00
244	42	11	2025-11-15	present	2025-11-15 02:21:42.499146+00	2025-11-15 07:13:23.388553+00	4.86	42	2025-11-15 02:21:42.499146+00	182.253.63.30	\N	attendances/42/check_in/2025-11-15/e1a8e6b4-d3bb-4ef2-9827-40b139261592.jpeg	2025-11-15 07:13:23.388553+00	182.253.63.30	\N	attendances/42/check_out/2025-11-15/ad372a00-fae8-4415-a44c-ff6bebb973c2.jpeg	2025-11-15 02:21:43.710669+00	2025-11-15 07:13:24.547599+00	-5.38758320	105.28016510	Jalan Alam Cantik, Kalibalau Kencana, Bandar Lampung, Lampung, Sumatra, 35133, Indonesia	-5.38758040	105.28016410	Jalan Alam Cantik, Kalibalau Kencana, Bandar Lampung, Lampung, Sumatra, 35133, Indonesia	\N
854	13	20	2025-12-08	absent	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	2025-12-08 16:00:00.077288+00	2025-12-08 16:00:00.077297+00	\N	\N	\N	\N	\N	\N	\N
863	62	30	2025-12-08	absent	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	2025-12-08 16:00:00.293583+00	2025-12-08 16:00:00.293588+00	\N	\N	\N	\N	\N	\N	\N
956	24	31	2025-12-11	present	2025-12-11 02:13:43.478813+00	2025-12-11 10:50:59.112975+00	8.62	24	2025-12-11 02:13:43.478813+00	103.105.82.245	\N	attendances/24/check_in/2025-12-11/98f1d109-b8d9-47f7-81a7-7ebd057feb2f.jpeg	2025-12-11 10:50:59.112975+00	103.105.82.245	\N	attendances/24/check_out/2025-12-11/9aaffcb6-dc09-471d-bf55-c5b2e5481192.jpeg	2025-12-11 02:13:44.237076+00	2025-12-11 10:51:00.15807+00	-5.38758470	105.28015730	Jalan Alam Kurnia, Kalibalau Kencana, Bandar Lampung, Lampung, Sumatra, 35133, Indonesia	-5.38758530	105.28015960	Jalan Alam Kurnia, Kalibalau Kencana, Bandar Lampung, Lampung, Sumatra, 35133, Indonesia	0.00
963	63	25	2025-12-11	present	2025-12-11 05:51:31.569768+00	2025-12-11 13:27:19.551012+00	7.60	63	2025-12-11 05:51:31.569768+00	103.87.231.107	Telat ngurusin NA	attendances/63/check_in/2025-12-11/7fac4bec-e950-4030-9040-06b6f0d06076.jpeg	2025-12-11 13:27:19.551012+00	103.87.231.107	\N	attendances/63/check_out/2025-12-11/aa18ef80-8b56-445e-8404-1107b03d67ab.jpeg	2025-12-11 05:51:34.211059+00	2025-12-11 13:27:22.394149+00	-5.02823010	104.30404580	Jalan Raya Serengit, Mekar Sari, Lampung Barat, Lampung, Sumatra, Indonesia	-5.02823930	104.30404200	Jalan Raya Serengit, Mekar Sari, Lampung Barat, Lampung, Sumatra, Indonesia	0.00
949	52	24	2025-12-11	present	2025-12-11 01:31:06.92436+00	2025-12-11 13:35:13.27895+00	12.07	52	2025-12-11 01:31:06.92436+00	103.87.231.107	\N	attendances/52/check_in/2025-12-11/09cba217-ecd2-4c48-8a1e-e97a2f992bf9.jpeg	2025-12-11 13:35:13.27895+00	114.10.100.143	\N	attendances/52/check_out/2025-12-11/a097e21e-b631-4220-925a-0b5190442d6f.jpeg	2025-12-11 01:31:07.688537+00	2025-12-11 13:35:17.639973+00	-5.02822950	104.30404600	Jalan Raya Serengit, Mekar Sari, Lampung Barat, Lampung, Sumatra, Indonesia	-5.02823130	104.30404700	Jalan Raya Serengit, Mekar Sari, Lampung Barat, Lampung, Sumatra, Indonesia	0.00
957	20	31	2025-12-11	invalid	2025-12-11 02:19:52.937579+00	\N	\N	20	2025-12-11 02:19:52.937579+00	103.105.82.245	\N	attendances/20/check_in/2025-12-11/b7921260-eee0-4234-a530-1d0e93f1cad5.jpeg	\N	\N	\N	\N	2025-12-11 02:19:53.697472+00	2025-12-11 16:30:00.0492+00	-5.38761457	105.28006999	Jalan Alam Kurnia, Kalibalau Kencana, Bandar Lampung, Lampung, Sumatra, 35133, Indonesia	\N	\N	\N	\N
245	22	15	2025-11-15	present	2025-11-15 02:31:50.445944+00	2025-11-15 06:50:04.721631+00	4.30	22	2025-11-15 02:31:50.445944+00	182.253.63.30	\N	attendances/22/check_in/2025-11-15/69966bec-2bac-4032-8f36-da7eb7cc6995.jpeg	2025-11-15 06:50:04.721631+00	182.253.63.30	\N	attendances/22/check_out/2025-11-15/a9b230c4-b234-4b76-ba5e-e3542fd735ec.jpeg	2025-11-15 02:31:51.596124+00	2025-11-15 06:50:05.406256+00	-5.38758940	105.28015430	Jalan Alam Kurnia, Kalibalau Kencana, Bandar Lampung, Lampung, Sumatra, 35133, Indonesia	-5.37943480	105.27800970	Stadion Way Halim, Way Halim Permai, Bandar Lampung, Lampung, Sumatra, 35133, Indonesia	\N
250	15	12	2025-11-15	present	2025-11-15 08:53:32.769778+00	2025-11-15 08:53:50.688331+00	0.00	15	2025-11-15 08:53:32.769778+00	182.3.105.170	\N	attendances/15/check_in/2025-11-15/6471d669-292b-4245-86ed-4a6a11c65d3d.jpeg	2025-11-15 08:53:50.688331+00	182.3.105.170	\N	attendances/15/check_out/2025-11-15/7cb68747-ac7e-4c4c-902c-c4b4792b0b8d.jpeg	2025-11-15 08:53:34.003181+00	2025-11-15 08:53:51.414118+00	-5.37564150	105.29489540	Jalan Mayor Jenderal Haji M. Ryacudu, Bandar Lampung, Lampung, Sumatra, 35131, Indonesia	-5.37564150	105.29489540	Jalan Mayor Jenderal Haji M. Ryacudu, Bandar Lampung, Lampung, Sumatra, 35131, Indonesia	\N
873	20	31	2025-12-08	absent	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	2025-12-08 16:00:00.34329+00	2025-12-08 16:00:00.3433+00	\N	\N	\N	\N	\N	\N	\N
950	40	28	2025-12-11	present	2025-12-11 01:32:50.033075+00	2025-12-11 10:18:36.893282+00	8.76	40	2025-12-11 01:32:50.033075+00	103.105.82.245	\N	attendances/40/check_in/2025-12-11/0fe004fc-0b84-4e26-8b79-ae5b17391fc4.jpeg	2025-12-11 10:18:36.893282+00	103.105.82.245	\N	attendances/40/check_out/2025-12-11/9f01c9f8-4773-49b3-a0b8-a6f98edf5d68.jpeg	2025-12-11 01:32:50.804384+00	2025-12-11 10:18:37.905555+00	-5.38759397	105.28016704	Jalan Alam Kurnia, Kalibalau Kencana, Bandar Lampung, Lampung, Sumatra, 35133, Indonesia	-5.39620980	105.27800970	Jalan Pulau Morotai, Tanjung Baru, Bandar Lampung, Lampung, Sumatra, 35227, Indonesia	0.00
952	23	33	2025-12-11	present	2025-12-11 01:56:04.50332+00	2025-12-11 10:58:11.003565+00	9.04	23	2025-12-11 01:56:04.50332+00	103.105.82.245	\N	attendances/23/check_in/2025-12-11/f556ad94-e8b3-4fe5-b7cf-a25018ae9794.jpeg	2025-12-11 10:58:11.003565+00	103.105.82.245	\N	attendances/23/check_out/2025-12-11/3cf16459-6736-4a79-8d4e-42f42382a1e3.jpeg	2025-12-11 01:56:05.374435+00	2025-12-11 10:58:12.130052+00	-5.38756996	105.28018086	Jalan Alam Cantik, Kalibalau Kencana, Bandar Lampung, Lampung, Sumatra, 35133, Indonesia	-5.38757491	105.28016702	Jalan Alam Cantik, Kalibalau Kencana, Bandar Lampung, Lampung, Sumatra, 35133, Indonesia	0.00
958	42	28	2025-12-11	invalid	2025-12-11 02:21:29.167917+00	\N	\N	42	2025-12-11 02:21:29.167917+00	182.3.100.118	\N	attendances/42/check_in/2025-12-11/ee3d37e6-b2a5-4544-be3a-7bb2ad6aa229.jpeg	\N	\N	\N	\N	2025-12-11 02:21:29.857461+00	2025-12-11 16:30:00.050157+00	-5.38758440	105.28015920	Jalan Alam Kurnia, Kalibalau Kencana, Bandar Lampung, Lampung, Sumatra, 35133, Indonesia	\N	\N	\N	\N
247	23	15	2025-11-15	present	2025-11-15 02:56:34.33841+00	2025-11-15 07:05:21.217148+00	4.15	23	2025-11-15 02:56:34.33841+00	140.213.112.47	\N	attendances/23/check_in/2025-11-15/b83bc119-0794-4fb1-8276-3d0cf78f0752.jpeg	2025-11-15 07:05:21.217148+00	140.213.115.157	\N	attendances/23/check_out/2025-11-15/9630f0e9-2a05-4000-91b5-df33ff473fcd.jpeg	2025-11-15 02:56:35.56194+00	2025-11-15 07:05:22.34267+00	-5.38754762	105.28012221	Jalan Alam Kurnia, Kalibalau Kencana, Bandar Lampung, Lampung, Sumatra, 35133, Indonesia	-5.38748993	105.28022446	Jalan Alam Cantik, Kalibalau Kencana, Bandar Lampung, Lampung, Sumatra, 35133, Indonesia	\N
874	39	32	2025-12-08	absent	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	2025-12-08 16:00:00.347223+00	2025-12-08 16:00:00.347227+00	\N	\N	\N	\N	\N	\N	\N
951	57	27	2025-12-11	present	2025-12-11 01:36:54.207215+00	2025-12-11 10:21:28.275701+00	8.74	57	2025-12-11 01:36:54.207215+00	103.144.14.2	pagar alam	attendances/57/check_in/2025-12-11/ae1636b8-2efb-4491-8360-1c0771eba255.jpeg	2025-12-11 10:21:28.275701+00	103.144.14.2	pagar alam	attendances/57/check_out/2025-12-11/498ed8c7-bda4-4bec-a177-6c35ab5130d5.jpeg	2025-12-11 01:36:55.252153+00	2025-12-11 10:21:29.107208+00	-4.05604359	103.29808579	Rantau Unji, Dempo Tengah, Pagar Alam, Sumatera Selatan, Sumatra, Indonesia	-4.05597426	103.29806414	Rantau Unji, Dempo Tengah, Pagar Alam, Sumatera Selatan, Sumatra, Indonesia	0.00
960	50	23	2025-12-11	present	2025-12-11 02:28:31.867033+00	2025-12-11 12:41:25.902105+00	10.22	50	2025-12-11 02:28:31.867033+00	114.10.102.209	\N	attendances/50/check_in/2025-12-11/7d04f651-28eb-4592-a5d6-31bcb02bbd7f.jpeg	2025-12-11 12:41:25.902105+00	114.10.100.53	\N	attendances/50/check_out/2025-12-11/cd41976c-8778-4cd8-b394-72e189855fcf.jpeg	2025-12-11 02:28:32.751254+00	2025-12-11 12:41:28.358121+00	-5.42952000	104.73404830	Gisting Bawah, Tanggamus, Lampung, Sumatra, Indonesia	-5.42949830	104.73429670	Gisting Bawah, Tanggamus, Lampung, Sumatra, Indonesia	0.00
263	13	10	2025-11-15	absent	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	2025-11-15 16:00:01.724719+00	2025-11-15 16:00:01.724724+00	\N	\N	\N	\N	\N	\N	\N
264	14	11	2025-11-15	absent	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	2025-11-15 16:00:01.754257+00	2025-11-15 16:00:01.754263+00	\N	\N	\N	\N	\N	\N	\N
270	20	14	2025-11-15	absent	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	2025-11-15 16:00:02.038277+00	2025-11-15 16:00:02.038282+00	\N	\N	\N	\N	\N	\N	\N
271	39	17	2025-11-15	hybrid	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	2025-11-15 16:00:02.18532+00	2025-11-15 16:00:02.185326+00	\N	\N	\N	\N	\N	\N	\N
272	43	17	2025-11-15	hybrid	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	2025-11-15 16:00:02.276044+00	2025-11-15 16:00:02.276049+00	\N	\N	\N	\N	\N	\N	\N
282	15	12	2025-11-17	present	2025-11-17 04:45:24.263979+00	2025-11-17 09:29:32.953082+00	4.74	15	2025-11-17 04:45:24.263979+00	182.3.100.238	Lupa cekin	attendances/15/check_in/2025-11-17/3baa748e-2241-45bd-9830-51296b603420.jpeg	2025-11-17 09:29:32.953082+00	182.3.100.211	\N	attendances/15/check_out/2025-11-17/6377b4ce-4901-4f40-8c34-2c063eb083c3.jpeg	2025-11-17 04:45:25.462169+00	2025-11-17 09:29:34.441051+00	-5.38749830	105.28009990	Jalan Alam Cantik, Kalibalau Kencana, Bandar Lampung, Lampung, Sumatra, 35133, Indonesia	-5.38749830	105.28009990	Jalan Alam Cantik, Kalibalau Kencana, Bandar Lampung, Lampung, Sumatra, 35133, Indonesia	\N
277	42	11	2025-11-17	present	2025-11-17 02:30:31.061433+00	2025-11-17 10:05:17.882348+00	7.58	42	2025-11-17 02:30:31.061433+00	182.253.63.30	\N	attendances/42/check_in/2025-11-17/b129f61c-ed76-4d11-b748-abfa8a97c06d.jpeg	2025-11-17 10:05:17.882348+00	182.253.63.30	\N	attendances/42/check_out/2025-11-17/093ad837-9664-4a3e-8e01-c2e1c00118ba.jpeg	2025-11-17 02:30:32.265074+00	2025-11-17 10:05:19.363925+00	-5.38765290	105.28013580	Jalan Alam Kurnia, Kalibalau Kencana, Bandar Lampung, Lampung, Sumatra, 35133, Indonesia	-5.38757670	105.28015040	Jalan Alam Kurnia, Kalibalau Kencana, Bandar Lampung, Lampung, Sumatra, 35133, Indonesia	\N
276	24	15	2025-11-17	present	2025-11-17 02:25:56.649014+00	2025-11-17 10:11:03.544795+00	7.75	24	2025-11-17 02:25:56.649014+00	182.253.63.30	\N	attendances/24/check_in/2025-11-17/0fb17a67-7f44-4ebe-aaf7-888a20c6934a.jpeg	2025-11-17 10:11:03.544795+00	182.253.63.30	\N	attendances/24/check_out/2025-11-17/bdb8517b-0674-41c1-aa0e-487ae72f0f80.jpeg	2025-11-17 02:25:57.394551+00	2025-11-17 10:11:04.664559+00	-5.40999680	105.26720000	Jalan Hayam Wuruk, Gunung Sari, Bandar Lampung, Lampung, Sumatra, 35121, Indonesia	-5.40999680	105.26720000	Jalan Hayam Wuruk, Gunung Sari, Bandar Lampung, Lampung, Sumatra, 35121, Indonesia	\N
275	23	15	2025-11-17	present	2025-11-17 02:21:50.168865+00	2025-11-17 10:25:02.77586+00	8.05	23	2025-11-17 02:21:50.168865+00	140.213.111.238	\N	attendances/23/check_in/2025-11-17/f16eafd8-0a09-4b31-9f26-d267af509595.jpeg	2025-11-17 10:25:02.77586+00	182.253.63.30	\N	attendances/23/check_out/2025-11-17/15cb9a22-314c-45d5-98f9-680ba12d25f8.jpeg	2025-11-17 02:21:51.357069+00	2025-11-17 10:25:04.366662+00	-5.38757848	105.28017569	Jalan Alam Cantik, Kalibalau Kencana, Bandar Lampung, Lampung, Sumatra, 35133, Indonesia	-5.38756310	105.28019779	Jalan Alam Cantik, Kalibalau Kencana, Bandar Lampung, Lampung, Sumatra, 35133, Indonesia	\N
279	22	15	2025-11-17	present	2025-11-17 02:51:32.103893+00	2025-11-17 10:29:22.805521+00	7.63	22	2025-11-17 02:51:32.103893+00	182.253.63.30	\N	attendances/22/check_in/2025-11-17/773fc6e5-25d7-4e30-b507-cfb54d78a7bd.jpeg	2025-11-17 10:29:22.805521+00	182.253.63.30	\N	attendances/22/check_out/2025-11-17/9c99d2d5-8377-459a-bf22-b152def355a6.jpeg	2025-11-17 02:51:33.203029+00	2025-11-17 10:29:23.609879+00	-5.39510060	105.27800960	Jalan Pulau Morotai, Kalibalau Kencana, Bandar Lampung, Lampung, Sumatra, 35133, Indonesia	-5.39510060	105.27800960	Jalan Pulau Morotai, Kalibalau Kencana, Bandar Lampung, Lampung, Sumatra, 35133, Indonesia	\N
274	40	11	2025-11-17	present	2025-11-17 02:09:24.617061+00	2025-11-17 11:17:42.690269+00	9.14	40	2025-11-17 02:09:24.617061+00	182.253.63.30	\N	attendances/40/check_in/2025-11-17/5ccfb1b6-ed1d-4a27-ab2e-f5915a5c59e1.jpeg	2025-11-17 11:17:42.690269+00	114.125.236.50	Dinas ke ulubelu	attendances/40/check_out/2025-11-17/a1c5b270-cb95-4c51-832c-96d7bc97cf29.jpeg	2025-11-17 02:09:25.438152+00	2025-11-17 11:17:43.850587+00	-5.39510060	105.27800960	Jalan Pulau Morotai, Kalibalau Kencana, Bandar Lampung, Lampung, Sumatra, 35133, Indonesia	-5.31024395	104.55968784	Pagaralam Ulubelu, Tanggamus, Lampung, Sumatra, Indonesia	\N
281	44	17	2025-11-17	present	2025-11-17 04:24:36.685781+00	2025-11-17 13:59:36.953708+00	9.58	44	2025-11-17 04:24:36.685781+00	182.253.63.30	\N	attendances/44/check_in/2025-11-17/1c7df6d3-4fb3-4af9-8fcf-c99bff92ed90.jpeg	2025-11-17 13:59:36.953708+00	182.253.63.30	\N	attendances/44/check_out/2025-11-17/969797f1-19a3-4a5b-bb0e-be5b6806b994.jpeg	2025-11-17 04:24:38.512317+00	2025-11-17 13:59:38.295979+00	-5.38765280	105.28013610	Jalan Alam Kurnia, Kalibalau Kencana, Bandar Lampung, Lampung, Sumatra, 35133, Indonesia	-5.38758040	105.28016440	Jalan Alam Cantik, Kalibalau Kencana, Bandar Lampung, Lampung, Sumatra, 35133, Indonesia	\N
278	41	12	2025-11-17	present	2025-11-17 02:44:10.593778+00	2025-11-17 13:59:42.916714+00	11.26	41	2025-11-17 02:44:10.593778+00	182.253.63.30	\N	attendances/41/check_in/2025-11-17/ed267289-b65e-4021-ab91-ac6751fdd493.jpeg	2025-11-17 13:59:42.916714+00	182.253.63.30	\N	attendances/41/check_out/2025-11-17/9336e51a-689c-4663-8847-f08a40fe6222.jpeg	2025-11-17 02:44:11.794294+00	2025-11-17 13:59:44.011222+00	-5.38764500	105.28013940	Jalan Alam Kurnia, Kalibalau Kencana, Bandar Lampung, Lampung, Sumatra, 35133, Indonesia	-5.38757870	105.28015790	Jalan Alam Cantik, Kalibalau Kencana, Bandar Lampung, Lampung, Sumatra, 35133, Indonesia	\N
295	13	10	2025-11-17	absent	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	2025-11-17 16:00:00.491012+00	2025-11-17 16:00:00.491015+00	\N	\N	\N	\N	\N	\N	\N
273	14	11	2025-11-17	invalid	2025-11-17 02:07:22.223663+00	\N	\N	14	2025-11-17 02:07:22.223663+00	182.253.63.30	\N	attendances/14/check_in/2025-11-17/3da9c5b7-c846-4f99-9a7f-e92581f6f397.jpeg	\N	\N	\N	\N	2025-11-17 02:07:23.851891+00	2025-11-17 16:59:00.072707+00	-5.39510060	105.27800960	Jalan Pulau Morotai, Kalibalau Kencana, Bandar Lampung, Lampung, Sumatra, 35133, Indonesia	\N	\N	\N	\N
280	20	14	2025-11-17	invalid	2025-11-17 02:55:55.679077+00	\N	\N	20	2025-11-17 02:55:55.679077+00	182.253.63.30	\N	attendances/20/check_in/2025-11-17/1736aab7-7946-4a26-8149-aacb4137fc97.jpeg	\N	\N	\N	\N	2025-11-17 02:55:56.517416+00	2025-11-17 16:59:00.091119+00	-5.39510060	105.27800960	Jalan Pulau Morotai, Kalibalau Kencana, Bandar Lampung, Lampung, Sumatra, 35133, Indonesia	\N	\N	\N	\N
309	41	12	2025-11-18	present	2025-11-18 02:46:37.667366+00	2025-11-18 10:20:48.891491+00	7.57	41	2025-11-18 02:46:37.667366+00	182.253.63.30	\N	attendances/41/check_in/2025-11-18/b7f67ad8-b764-40dd-bb1a-684316c87635.jpeg	2025-11-18 10:20:48.891491+00	182.3.101.15	\N	attendances/41/check_out/2025-11-18/13421f68-5e45-4f1f-bea7-528954c8d781.jpeg	2025-11-18 02:46:38.363072+00	2025-11-18 10:20:49.658699+00	-5.38757970	105.28016120	Jalan Alam Cantik, Kalibalau Kencana, Bandar Lampung, Lampung, Sumatra, 35133, Indonesia	-5.38758560	105.28015960	Jalan Alam Kurnia, Kalibalau Kencana, Bandar Lampung, Lampung, Sumatra, 35133, Indonesia	\N
875	43	32	2025-12-08	present	2025-12-08 09:00:00+00	2025-12-08 17:00:00+00	8.00	\N	\N	\N	Diubah oleh Richard Arya Winarta pada 09-12-2025 15:12:00 WIB	\N	\N	\N	Diubah oleh Richard Arya Winarta pada 09-12-2025 15:12:00 WIB	\N	2025-12-08 16:00:00.352271+00	2025-12-09 15:12:00.221687+00	\N	\N	\N	\N	\N	\N	0.00
964	58	27	2025-12-11	present	2025-12-11 10:07:05.223409+00	2025-12-11 10:08:10.992747+00	0.02	58	2025-12-11 10:07:05.223409+00	103.144.14.2	Uji coba absen hari pertama	attendances/58/check_in/2025-12-11/e3bbe56e-c898-4d2a-a6f5-f6d58ca443af.jpeg	2025-12-11 10:08:10.992747+00	103.144.14.2	\N	attendances/58/check_out/2025-12-11/eb94a560-ac5a-4353-aa71-1e42ca2cd938.jpeg	2025-12-11 10:07:06.729082+00	2025-12-11 10:08:11.990747+00	-4.05607780	103.29806730	Rantau Unji, Dempo Tengah, Pagar Alam, Sumatera Selatan, Sumatra, Indonesia	-4.05606980	103.29806650	Rantau Unji, Dempo Tengah, Pagar Alam, Sumatera Selatan, Sumatra, Indonesia	0.00
967	54	25	2025-12-11	absent	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	2025-12-11 16:00:00.16273+00	2025-12-11 16:00:00.162735+00	\N	\N	\N	\N	\N	\N	\N
972	39	32	2025-12-11	hybrid	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	2025-12-11 16:00:00.231345+00	2025-12-11 16:00:00.23135+00	\N	\N	\N	\N	\N	\N	\N
975	60	29	2025-12-12	present	2025-12-12 00:29:45.788719+00	2025-12-12 12:04:52.488359+00	11.59	60	2025-12-12 00:29:45.788719+00	103.145.34.18	\N	attendances/60/check_in/2025-12-12/33dcf098-949e-4f21-9435-c41fa48b929c.jpeg	2025-12-12 12:04:52.488359+00	103.145.34.18	\N	attendances/60/check_out/2025-12-12/34f7c5c7-9799-4d60-b213-6c119909885f.jpeg	2025-12-12 00:29:46.815311+00	2025-12-12 12:04:53.466641+00	-5.42616330	104.73805500	Gisting Bawah, Tanggamus, Lampung, Sumatra, Indonesia	-5.42568810	104.73794100	Kota Dalam, Tanggamus, Lampung, Sumatra, Indonesia	0.00
978	15	21	2025-12-12	present	2025-12-12 01:05:39.248663+00	2025-12-12 12:32:26.907572+00	11.45	15	2025-12-12 01:05:39.248663+00	103.144.14.2	\N	attendances/15/check_in/2025-12-12/2cec8f3f-e828-4134-bc5c-9f79dd4aa362.jpeg	2025-12-12 12:32:26.907572+00	114.125.236.155	\N	attendances/15/check_out/2025-12-12/88c824fb-10e6-470c-ac75-980c61d27d22.jpeg	2025-12-12 01:05:39.950281+00	2025-12-12 12:32:28.149989+00	-4.05607160	103.29807100	Rantau Unji, Dempo Tengah, Pagar Alam, Sumatera Selatan, Sumatra, Indonesia	-4.05607070	103.29806540	Rantau Unji, Dempo Tengah, Pagar Alam, Sumatera Selatan, Sumatra, Indonesia	0.00
307	39	17	2025-11-18	present	2025-11-18 02:35:04.106487+00	2025-11-18 08:22:52.781036+00	5.80	39	2025-11-18 02:35:04.106487+00	182.253.63.30	\N	attendances/39/check_in/2025-11-18/7c18a300-88f3-4306-a16c-6b97225af678.jpeg	2025-11-18 08:22:52.781036+00	182.253.63.30	\N	attendances/39/check_out/2025-11-18/bd4e24a2-88f1-45da-92e8-a1e084a2d119.jpeg	2025-11-18 02:35:05.217788+00	2025-11-18 08:22:54.24558+00	-5.38757870	105.28016020	Jalan Alam Cantik, Kalibalau Kencana, Bandar Lampung, Lampung, Sumatra, 35133, Indonesia	-5.38757930	105.28016150	Jalan Alam Cantik, Kalibalau Kencana, Bandar Lampung, Lampung, Sumatra, 35133, Indonesia	\N
303	40	11	2025-11-18	present	2025-11-18 00:51:55.759144+00	2025-11-18 09:31:56.584024+00	8.67	40	2025-11-18 00:51:55.759144+00	182.3.103.166	Dinas ulubelu	attendances/40/check_in/2025-11-18/6d3dc53b-686c-4614-9d4b-be3d3b862345.jpeg	2025-11-18 09:31:56.584024+00	182.253.63.30	\N	attendances/40/check_out/2025-11-18/5eaa6493-4df0-4e61-9df1-e73a0a1434f1.jpeg	2025-11-18 00:51:57.370737+00	2025-11-18 09:31:57.364603+00	-5.31063206	104.55583275	Jalan Ngarip - Ulo Semong, Pagaralam Ulubelu, Tanggamus, Lampung, Sumatra, Indonesia	-5.38748121	105.28024286	Jalan Alam Cantik, Kalibalau Kencana, Bandar Lampung, Lampung, Sumatra, 35133, Indonesia	\N
948	51	23	2025-12-11	present	2025-12-11 01:21:37.957239+00	2025-12-11 10:30:31.75106+00	9.15	51	2025-12-11 01:21:37.957239+00	103.59.44.25	\N	attendances/51/check_in/2025-12-11/52df53da-763e-4798-8f6e-b14fa24b70e7.jpeg	2025-12-11 10:30:31.75106+00	103.59.44.25	\N	attendances/51/check_out/2025-12-11/dcc32e9b-3af7-4ad6-bd1e-605bacf4ae24.jpeg	2025-12-11 01:21:38.641707+00	2025-12-11 10:30:32.875124+00	-5.43053500	104.73911500	Gisting Bawah, Tanggamus, Lampung, Sumatra, Indonesia	-5.43057980	104.73918580	Gisting Bawah, Tanggamus, Lampung, Sumatra, Indonesia	0.00
954	44	34	2025-12-11	present	2025-12-11 01:57:55.502278+00	2025-12-11 14:50:47.629268+00	12.88	44	2025-12-11 01:57:55.502278+00	114.10.100.193	Gudang ARGA Lambar	attendances/44/check_in/2025-12-11/20b3bd47-c430-4e09-81ab-5837f24b6d76.jpeg	2025-12-11 14:50:47.629268+00	114.10.102.12	\N	attendances/44/check_out/2025-12-11/8dfe15fd-e69a-4423-ae1a-b20df50aea1b.jpeg	2025-12-11 01:57:56.203899+00	2025-12-11 14:50:48.704591+00	-5.02796500	104.30415830	Lampung Barat, Lampung, Sumatra, Indonesia	-5.37166080	105.24928550	Gang Surya Kencana 1, Sepang Jaya, Bandar Lampung, Lampung, Sumatra, 35141, Indonesia	0.00
968	62	30	2025-12-11	absent	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	2025-12-11 16:00:00.17306+00	2025-12-11 16:00:00.173064+00	\N	\N	\N	\N	\N	\N	\N
973	43	32	2025-12-11	hybrid	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	2025-12-11 16:00:00.236747+00	2025-12-11 16:00:00.23675+00	\N	\N	\N	\N	\N	\N	\N
977	45	21	2025-12-12	present	2025-12-12 01:05:19.209538+00	2025-12-12 13:06:46.330635+00	12.02	45	2025-12-12 01:05:19.209538+00	103.144.14.2	\N	attendances/45/check_in/2025-12-12/f89bb619-98e2-42b5-929a-70a046658818.jpeg	2025-12-12 13:06:46.330635+00	182.1.238.163	\N	attendances/45/check_out/2025-12-12/c3680003-2b27-44cb-a910-94b8063f6a6c.jpeg	2025-12-12 01:05:20.057331+00	2025-12-12 13:06:47.358166+00	-4.05603230	103.29810899	Rantau Unji, Dempo Tengah, Pagar Alam, Sumatera Selatan, Sumatra, Indonesia	-4.05607160	103.29806980	Rantau Unji, Dempo Tengah, Pagar Alam, Sumatera Selatan, Sumatra, Indonesia	0.00
979	49	23	2025-12-12	present	2025-12-12 01:16:14.822282+00	2025-12-12 14:38:44.881345+00	13.38	49	2025-12-12 01:16:14.822282+00	103.59.44.25	\N	attendances/49/check_in/2025-12-12/5cc9151b-25e9-4ae1-96c1-eab585646254.jpeg	2025-12-12 14:38:44.881345+00	182.3.103.215	Maaf tadi lupa cekout bu🙏	attendances/49/check_out/2025-12-12/f4878a2e-bb5b-4b61-9ce8-3c23ffb118e0.jpg	2025-12-12 01:16:15.829464+00	2025-12-12 14:38:46.173659+00	-5.43041700	104.73899670	Gisting Bawah, Tanggamus, Lampung, Sumatra, Indonesia	-5.42144520	104.73164700	Tanggamus, Lampung, Sumatra, Indonesia	0.00
304	15	12	2025-11-18	present	2025-11-18 01:29:50.830001+00	2025-11-18 09:29:46.863932+00	8.00	15	2025-11-18 01:29:50.830001+00	182.3.101.77	\N	attendances/15/check_in/2025-11-18/bfcc7993-23dc-4d51-a1ef-ee58844138e3.jpeg	2025-11-18 09:29:46.863932+00	182.3.104.46	\N	attendances/15/check_out/2025-11-18/d4f4fa46-ca1c-4e6d-9497-0527d25012c0.jpeg	2025-11-18 01:29:51.983064+00	2025-11-18 09:29:48.01798+00	-5.30983070	104.55893220	Pagaralam Ulubelu, Tanggamus, Lampung, Sumatra, Indonesia	-5.38757860	105.28016050	Jalan Alam Cantik, Kalibalau Kencana, Bandar Lampung, Lampung, Sumatra, 35133, Indonesia	\N
965	46	21	2025-12-11	absent	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	2025-12-11 16:00:00.100287+00	2025-12-11 16:00:00.100296+00	\N	\N	\N	\N	\N	\N	\N
970	56	27	2025-12-11	absent	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	2025-12-11 16:00:00.207915+00	2025-12-11 16:00:00.207919+00	\N	\N	\N	\N	\N	\N	\N
974	61	29	2025-12-12	present	2025-12-12 00:06:29.048943+00	2025-12-12 08:56:40.95454+00	8.84	61	2025-12-12 00:06:29.048943+00	114.10.102.55	\N	attendances/61/check_in/2025-12-12/1fe8051d-dde3-4e57-9c31-ec04efafef37.jpeg	2025-12-12 08:56:40.95454+00	114.10.100.207	\N	attendances/61/check_out/2025-12-12/4e6a0f46-198a-468a-94b0-c05e49461cdc.jpeg	2025-12-12 00:06:30.459354+00	2025-12-12 08:56:42.645356+00	-5.06628170	104.13279670	Lampung Barat, Lampung, Sumatra, Indonesia	-5.05175350	104.10773390	Gang Buntu, Liwa, Lampung Barat, Lampung, Sumatra, 34812, Indonesia	0.00
976	64	24	2025-12-12	present	2025-12-12 01:01:05.145835+00	2025-12-12 14:48:11.973291+00	13.79	64	2025-12-12 01:01:05.145835+00	110.137.39.211	\N	attendances/64/check_in/2025-12-12/528b171b-a7d0-4787-9937-16b909d2ad39.jpeg	2025-12-12 14:48:11.973291+00	110.137.39.211	\N	attendances/64/check_out/2025-12-12/d5a56ad5-53a2-4460-b6da-e5a59e43c046.jpeg	2025-12-12 01:01:06.140195+00	2025-12-12 14:48:13.644093+00	-4.85922435	104.93114502	Tanjung Harapan, Lampung Utara, Lampung, Sumatra, 34511, Indonesia	-4.85922216	104.93114676	Tanjung Harapan, Lampung Utara, Lampung, Sumatra, 34511, Indonesia	0.00
310	24	15	2025-11-18	present	2025-11-18 02:53:42.671663+00	2025-11-18 10:15:56.471428+00	7.37	24	2025-11-18 02:53:42.671663+00	182.253.63.30	\N	attendances/24/check_in/2025-11-18/3d34e243-8160-4bc4-a519-81c7bf8f59e4.jpeg	2025-11-18 10:15:56.471428+00	182.253.63.30	\N	attendances/24/check_out/2025-11-18/e74c20b6-e160-45d7-b7f9-10c7be31b4af.jpeg	2025-11-18 02:53:43.866208+00	2025-11-18 10:15:57.772164+00	-5.37723880	105.25460030	Pelita, Bandar Lampung, Lampung, Sumatra, 35142, Indonesia	-5.37723880	105.25460030	Pelita, Bandar Lampung, Lampung, Sumatra, 35142, Indonesia	\N
305	20	14	2025-11-18	present	2025-11-18 02:26:34.615998+00	2025-11-18 10:37:25.240733+00	8.18	20	2025-11-18 02:26:34.615998+00	114.10.103.154	\N	attendances/20/check_in/2025-11-18/e7c67f1d-7916-4e5b-a206-d668018f0b68.jpeg	2025-11-18 10:37:25.240733+00	182.253.63.30	\N	attendances/20/check_out/2025-11-18/b6b2279f-0300-4c68-bfc9-f4cfdaaf01d4.jpeg	2025-11-18 02:26:35.668003+00	2025-11-18 10:37:25.955425+00	-5.38705920	105.25736960	Gang Manggis, Sidodadi, Bandar Lampung, Lampung, Sumatra, 35123, Indonesia	-5.40594350	105.25606330	Gang Empang, Pasir Gintung, Bandar Lampung, Lampung, Sumatra, 35121, Indonesia	\N
312	44	17	2025-11-18	present	2025-11-18 03:31:12.807379+00	2025-11-18 15:09:41.033036+00	11.64	44	2025-11-18 03:31:12.807379+00	114.10.102.184	\N	attendances/44/check_in/2025-11-18/8076bc27-afb8-448b-8712-9847b9b77795.jpeg	2025-11-18 15:09:41.033036+00	114.10.102.184	\N	attendances/44/check_out/2025-11-18/52c0de1b-07b9-4645-b3a7-7463fa78c4c9.jpeg	2025-11-18 03:31:13.885777+00	2025-11-18 15:09:42.475173+00	-5.38758220	105.28016530	Jalan Alam Cantik, Kalibalau Kencana, Bandar Lampung, Lampung, Sumatra, 35133, Indonesia	-5.38289100	105.28900960	Kalibalau Kencana, Bandar Lampung, Lampung, Sumatra, 35133, Indonesia	\N
966	59	29	2025-12-11	absent	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	2025-12-11 16:00:00.140423+00	2025-12-11 16:00:00.140428+00	\N	\N	\N	\N	\N	\N	\N
971	47	22	2025-12-11	absent	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	2025-12-11 16:00:00.217269+00	2025-12-11 16:00:00.217274+00	\N	\N	\N	\N	\N	\N	\N
311	22	15	2025-11-18	present	2025-11-18 02:57:24.738964+00	2025-11-18 09:42:52.030922+00	6.76	22	2025-11-18 02:57:24.738964+00	182.253.63.30	\N	attendances/22/check_in/2025-11-18/5303fe34-9e27-4e4a-9391-ec03e4534a6a.jpeg	2025-11-18 09:42:52.030922+00	182.253.63.30	\N	attendances/22/check_out/2025-11-18/71ec1c41-e10f-44ca-a51c-3589bdd62aa3.jpeg	2025-11-18 02:57:25.528971+00	2025-11-18 09:42:53.141002+00	-5.37723880	105.25460030	Pelita, Bandar Lampung, Lampung, Sumatra, 35142, Indonesia	-5.40594350	105.25606330	Gang Empang, Pasir Gintung, Bandar Lampung, Lampung, Sumatra, 35121, Indonesia	\N
306	23	15	2025-11-18	present	2025-11-18 02:27:47.85825+00	2025-11-18 10:33:56.57794+00	8.10	23	2025-11-18 02:27:47.85825+00	140.213.157.48	\N	attendances/23/check_in/2025-11-18/135fb120-4471-4740-b484-5c781c7e7199.jpeg	2025-11-18 10:33:56.57794+00	140.213.113.13	\N	attendances/23/check_out/2025-11-18/97982a5f-9ed6-4abe-be5f-02a47aa5763d.jpeg	2025-11-18 02:27:48.602702+00	2025-11-18 10:33:57.97539+00	-5.38755221	105.28012090	Jalan Alam Kurnia, Kalibalau Kencana, Bandar Lampung, Lampung, Sumatra, 35133, Indonesia	-5.38751884	105.28014956	Jalan Alam Cantik, Kalibalau Kencana, Bandar Lampung, Lampung, Sumatra, 35133, Indonesia	\N
885	44	34	2025-12-09	present	2025-12-09 02:54:04.010228+00	2025-12-09 10:34:39.840925+00	7.68	44	2025-12-09 02:54:04.010228+00	103.105.82.245	\N	attendances/44/check_in/2025-12-09/2452cbcd-8ba7-4de5-90d3-e3a80cb76d18.jpeg	2025-12-09 10:34:39.840925+00	103.105.82.245	\N	attendances/44/check_out/2025-12-09/fc9f5811-60b8-4097-a9f8-a1e47a42502a.jpeg	2025-12-09 02:54:05.098874+00	2025-12-09 10:34:40.902561+00	-5.38758710	105.28015690	Jalan Alam Kurnia, Kalibalau Kencana, Bandar Lampung, Lampung, Sumatra, 35133, Indonesia	-5.38758160	105.28016220	Jalan Alam Cantik, Kalibalau Kencana, Bandar Lampung, Lampung, Sumatra, 35133, Indonesia	0.00
878	24	31	2025-12-09	invalid	2025-12-09 01:49:16.558037+00	\N	\N	24	2025-12-09 01:49:16.558037+00	103.105.82.245	\N	attendances/24/check_in/2025-12-09/06df2882-ba42-4ebd-bf92-b59ff0bd451f.jpeg	\N	\N	\N	\N	2025-12-09 01:49:18.101113+00	2025-12-09 16:30:00.009958+00	-5.38753330	105.28019240	Jalan Alam Cantik, Kalibalau Kencana, Bandar Lampung, Lampung, Sumatra, 35133, Indonesia	\N	\N	\N	\N
969	55	27	2025-12-11	absent	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	2025-12-11 16:00:00.193716+00	2025-12-11 16:00:00.19372+00	\N	\N	\N	\N	\N	\N	\N
308	42	11	2025-11-18	present	2025-11-18 02:43:13.29697+00	2025-11-18 10:17:57.206378+00	7.58	42	2025-11-18 02:43:13.29697+00	182.253.63.30	\N	attendances/42/check_in/2025-11-18/de0bfb1f-5bbd-4793-94e2-c9287d721090.jpeg	2025-11-18 10:17:57.206378+00	182.253.63.30	\N	attendances/42/check_out/2025-11-18/e8193b6e-19a2-44cb-8948-cc2b524c3e34.jpeg	2025-11-18 02:43:14.418792+00	2025-11-18 10:17:58.037478+00	-5.38758050	105.28016380	Jalan Alam Cantik, Kalibalau Kencana, Bandar Lampung, Lampung, Sumatra, 35133, Indonesia	-5.38759770	105.28015670	Jalan Alam Kurnia, Kalibalau Kencana, Bandar Lampung, Lampung, Sumatra, 35133, Indonesia	\N
879	15	21	2025-12-09	present	2025-12-09 02:08:54.741764+00	2025-12-09 07:56:52.179659+00	5.80	15	2025-12-09 02:08:54.741764+00	103.105.82.245	\N	attendances/15/check_in/2025-12-09/2047ba42-0f9a-4d9d-8410-a5928e52f16e.jpeg	2025-12-09 07:56:52.179659+00	103.105.82.245	\N	attendances/15/check_out/2025-12-09/5b9e3fee-4cd9-452e-959d-a8db94351b16.jpeg	2025-12-09 02:08:55.806943+00	2025-12-09 07:56:53.453255+00	-5.38765770	105.28016660	Jalan Alam Kurnia, Kalibalau Kencana, Bandar Lampung, Lampung, Sumatra, 35133, Indonesia	-5.38758330	105.28015730	Jalan Alam Kurnia, Kalibalau Kencana, Bandar Lampung, Lampung, Sumatra, 35133, Indonesia	0.00
880	20	31	2025-12-09	invalid	2025-12-09 02:12:52.892955+00	\N	\N	20	2025-12-09 02:12:52.892955+00	114.10.101.199	\N	attendances/20/check_in/2025-12-09/b556e116-1e04-491e-987d-01d8a047b8e6.jpeg	\N	\N	\N	\N	2025-12-09 02:12:53.713907+00	2025-12-09 16:30:00.011298+00	-5.36372200	105.28925300	Jalan Bunga Sedap Malam Raya, Way Dadi, Bandar Lampung, Lampung, Sumatra, 35139, Indonesia	\N	\N	\N	\N
980	51	23	2025-12-12	present	2025-12-12 01:21:05.858141+00	2025-12-12 10:29:03.423848+00	9.13	51	2025-12-12 01:21:05.858141+00	103.59.44.25	\N	attendances/51/check_in/2025-12-12/f95a5373-5422-46ac-a4fa-25e155325c93.jpeg	2025-12-12 10:29:03.423848+00	103.59.44.25	\N	attendances/51/check_out/2025-12-12/3816724c-171e-4b83-ba87-5671bf1b6dd7.jpeg	2025-12-12 01:21:06.701763+00	2025-12-12 10:29:04.368643+00	-5.43058380	104.73918210	Gisting Bawah, Tanggamus, Lampung, Sumatra, Indonesia	-5.43075180	104.73923450	Gisting Bawah, Tanggamus, Lampung, Sumatra, Indonesia	0.00
986	63	25	2025-12-12	present	2025-12-12 02:00:14.294894+00	2025-12-12 11:58:24.30626+00	9.97	63	2025-12-12 02:00:14.294894+00	103.87.231.107	\N	attendances/63/check_in/2025-12-12/2874336a-95dc-4e4b-a753-580082a19c60.jpeg	2025-12-12 11:58:24.30626+00	103.87.231.107	\N	attendances/63/check_out/2025-12-12/7c41dfa5-d37f-407e-88f6-a9c880030bb6.jpeg	2025-12-12 02:00:15.049039+00	2025-12-12 11:58:25.363279+00	-5.02823890	104.30404060	Jalan Raya Serengit, Mekar Sari, Lampung Barat, Lampung, Sumatra, Indonesia	-5.02823010	104.30403850	Jalan Raya Serengit, Mekar Sari, Lampung Barat, Lampung, Sumatra, Indonesia	0.00
997	54	25	2025-12-12	absent	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	2025-12-12 16:00:00.149572+00	2025-12-12 16:00:00.149577+00	\N	\N	\N	\N	\N	\N	\N
325	13	10	2025-11-18	absent	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	2025-11-18 16:00:00.556221+00	2025-11-18 16:00:00.556224+00	\N	\N	\N	\N	\N	\N	\N
326	14	11	2025-11-18	absent	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	2025-11-18 16:00:00.570167+00	2025-11-18 16:00:00.570172+00	\N	\N	\N	\N	\N	\N	\N
1002	24	31	2025-12-12	absent	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	2025-12-12 16:00:00.187886+00	2025-12-12 16:00:00.187889+00	\N	\N	\N	\N	\N	\N	\N
332	43	17	2025-11-18	hybrid	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	2025-11-18 16:00:00.607636+00	2025-11-18 16:00:00.607641+00	\N	\N	\N	\N	\N	\N	\N
340	40	11	2025-11-19	present	2025-11-19 03:34:59.962581+00	2025-11-19 09:34:09.592107+00	5.99	40	2025-11-19 03:34:59.962581+00	182.253.63.30	\N	attendances/40/check_in/2025-11-19/ecc2accf-fd4e-412b-bc21-9aa7db8695bd.jpeg	2025-11-19 09:34:09.592107+00	103.140.189.174	wfc dari jam 3	attendances/40/check_out/2025-11-19/82165e36-7c84-4c1a-8f01-f473c6a8b815.jpeg	2025-11-19 03:35:01.128636+00	2025-11-19 09:34:11.077193+00	-5.39279280	105.27142550	Jagabaya II, Bandar Lampung, Lampung, Sumatra, 35136, Indonesia	-5.38568030	105.25752630	Gang Cempaka, Sukamenanti, Bandar Lampung, Lampung, Sumatra, 35123, Indonesia	\N
334	42	11	2025-11-19	present	2025-11-19 02:20:07.122576+00	2025-11-19 10:17:38.008767+00	7.96	42	2025-11-19 02:20:07.122576+00	182.253.63.30	\N	attendances/42/check_in/2025-11-19/d29bb223-c7ca-47cc-8270-597a93a87cd5.jpeg	2025-11-19 10:17:38.008767+00	182.253.63.30	\N	attendances/42/check_out/2025-11-19/99a9e532-2e0c-4345-9606-3c7d5039874e.jpeg	2025-11-19 02:20:08.25047+00	2025-11-19 10:17:39.024166+00	-5.38764580	105.28013890	Jalan Alam Kurnia, Kalibalau Kencana, Bandar Lampung, Lampung, Sumatra, 35133, Indonesia	-5.38760290	105.28014230	Jalan Alam Kurnia, Kalibalau Kencana, Bandar Lampung, Lampung, Sumatra, 35133, Indonesia	\N
336	41	12	2025-11-19	present	2025-11-19 02:42:14.678762+00	2025-11-19 10:18:11.472864+00	7.60	41	2025-11-19 02:42:14.678762+00	182.253.63.30	\N	attendances/41/check_in/2025-11-19/0024da3c-3468-43cb-81ff-98f8fd036327.jpeg	2025-11-19 10:18:11.472864+00	182.253.63.30	\N	attendances/41/check_out/2025-11-19/6cc2dd6c-ec35-45c3-b4e9-ee694a78131b.jpeg	2025-11-19 02:42:15.81589+00	2025-11-19 10:18:12.190897+00	-5.38766480	105.28013640	Jalan Alam Kurnia, Kalibalau Kencana, Bandar Lampung, Lampung, Sumatra, 35133, Indonesia	-5.38758860	105.28015730	Jalan Alam Kurnia, Kalibalau Kencana, Bandar Lampung, Lampung, Sumatra, 35133, Indonesia	\N
342	14	11	2025-11-19	present	2025-11-19 08:01:37.960029+00	2025-11-19 10:24:22.656418+00	2.38	14	2025-11-19 08:01:37.960029+00	182.253.63.30	\N	attendances/14/check_in/2025-11-19/781d0b45-f51a-44b0-9aa5-3ca96898e481.jpeg	2025-11-19 10:24:22.656418+00	182.253.63.30	\N	attendances/14/check_out/2025-11-19/cd833fbd-5863-43e4-ab5d-4d06cc5516f0.jpeg	2025-11-19 08:01:39.535166+00	2025-11-19 10:24:26.377819+00	-5.39510060	105.27800960	Jalan Pulau Morotai, Kalibalau Kencana, Bandar Lampung, Lampung, Sumatra, 35133, Indonesia	-5.39510060	105.27800960	Jalan Pulau Morotai, Kalibalau Kencana, Bandar Lampung, Lampung, Sumatra, 35133, Indonesia	\N
333	24	15	2025-11-19	present	2025-11-19 01:52:55.91179+00	2025-11-19 10:35:58.771648+00	8.72	24	2025-11-19 01:52:55.91179+00	182.253.63.30	\N	attendances/24/check_in/2025-11-19/fb273ef2-fecf-4d11-b7e9-ce3e9f8afb8b.jpeg	2025-11-19 10:35:58.771648+00	182.253.63.30	\N	attendances/24/check_out/2025-11-19/eca23a0c-83fa-4fe0-84d8-7d88fe284f53.jpeg	2025-11-19 01:52:57.492583+00	2025-11-19 10:35:59.96993+00	-5.40999680	105.26720000	Jalan Hayam Wuruk, Gunung Sari, Bandar Lampung, Lampung, Sumatra, 35121, Indonesia	-5.38757230	105.28014570	Jalan Alam Kurnia, Kalibalau Kencana, Bandar Lampung, Lampung, Sumatra, 35133, Indonesia	\N
337	22	15	2025-11-19	present	2025-11-19 02:43:35.217397+00	2025-11-19 10:36:38.004388+00	7.88	22	2025-11-19 02:43:35.217397+00	182.253.63.30	\N	attendances/22/check_in/2025-11-19/29da002b-af8c-4f35-9da9-e661e00c08b3.jpeg	2025-11-19 10:36:38.004388+00	182.253.63.30	\N	attendances/22/check_out/2025-11-19/0fe58d5b-b9d5-4b78-9c96-d5863c1a5494.jpeg	2025-11-19 02:43:35.976614+00	2025-11-19 10:36:38.713319+00	-5.40594350	105.25606330	Gang Empang, Pasir Gintung, Bandar Lampung, Lampung, Sumatra, 35121, Indonesia	-5.40585980	105.25313730	Sawah Lama, Bandar Lampung, Lampung, Sumatra, 35112, Indonesia	\N
335	23	15	2025-11-19	present	2025-11-19 02:24:04.038853+00	2025-11-19 10:38:41.757668+00	8.24	23	2025-11-19 02:24:04.038853+00	140.213.156.1	\N	attendances/23/check_in/2025-11-19/0526b7e5-9d39-4b33-a7cf-56b8b6ecbaa3.jpeg	2025-11-19 10:38:41.757668+00	182.253.63.30	\N	attendances/23/check_out/2025-11-19/0dddd084-0493-4357-93c5-00bc43e88b65.jpeg	2025-11-19 02:24:04.979403+00	2025-11-19 10:38:42.56606+00	-5.38756289	105.28016364	Jalan Alam Cantik, Kalibalau Kencana, Bandar Lampung, Lampung, Sumatra, 35133, Indonesia	-5.38758684	105.28020829	Jalan Alam Cantik, Kalibalau Kencana, Bandar Lampung, Lampung, Sumatra, 35133, Indonesia	\N
338	20	14	2025-11-19	present	2025-11-19 02:50:36.205297+00	2025-11-19 12:54:03.656848+00	10.06	20	2025-11-19 02:50:36.205297+00	182.253.63.30	\N	attendances/20/check_in/2025-11-19/c0e64700-1059-4f30-8513-ac0bbb5f9932.jpeg	2025-11-19 12:54:03.656848+00	114.10.103.218	\N	attendances/20/check_out/2025-11-19/f42fa2c6-744b-45b2-8074-673c46f35c34.jpeg	2025-11-19 02:50:37.388137+00	2025-11-19 12:54:05.937815+00	-5.39279280	105.27142550	Jagabaya II, Bandar Lampung, Lampung, Sumatra, 35136, Indonesia	-5.39279280	105.27142550	Jagabaya II, Bandar Lampung, Lampung, Sumatra, 35136, Indonesia	\N
339	44	17	2025-11-19	present	2025-11-19 03:01:16.291284+00	2025-11-19 15:00:43.533825+00	11.99	44	2025-11-19 03:01:16.291284+00	182.253.63.30	\N	attendances/44/check_in/2025-11-19/77440c0d-a72c-488a-8fac-b2dae52303ce.jpeg	2025-11-19 15:00:43.533825+00	114.10.102.15	\N	attendances/44/check_out/2025-11-19/299eaae4-4092-4827-a895-ee72cc8f0e55.jpeg	2025-11-19 03:01:17.342757+00	2025-11-19 15:00:44.992155+00	-5.38758180	105.28016130	Jalan Alam Cantik, Kalibalau Kencana, Bandar Lampung, Lampung, Sumatra, 35133, Indonesia	-5.37270680	105.24939940	Gang Zakaria III, Sepang Jaya, Bandar Lampung, Lampung, Sumatra, 35148, Indonesia	\N
355	13	10	2025-11-19	absent	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	2025-11-19 16:00:00.532601+00	2025-11-19 16:00:00.532605+00	\N	\N	\N	\N	\N	\N	\N
372	20	14	2025-11-20	present	2025-11-20 08:18:23.523092+00	2025-11-20 10:14:22.941989+00	1.93	20	2025-11-20 08:18:23.523092+00	182.253.63.30	\N	attendances/20/check_in/2025-11-20/4b9c775c-3c02-4c77-b83a-13d60cb66b3e.jpeg	2025-11-20 10:14:22.941989+00	182.253.63.30	\N	attendances/20/check_out/2025-11-20/9d905993-a102-4b05-89c0-b33f255f40e3.jpeg	2025-11-20 08:18:25.048655+00	2025-11-20 10:14:24.049219+00	-5.37794940	105.25313730	Jalan Harapan II, Pelita, Bandar Lampung, Lampung, Sumatra, 35142, Indonesia	-5.37794940	105.25313730	Jalan Harapan II, Pelita, Bandar Lampung, Lampung, Sumatra, 35142, Indonesia	\N
369	22	15	2025-11-20	present	2025-11-20 03:09:58.823561+00	2025-11-20 10:22:32.07651+00	7.21	22	2025-11-20 03:09:58.823561+00	182.253.63.30	\N	attendances/22/check_in/2025-11-20/9caa064d-7161-4d40-a160-64e25d534f52.jpeg	2025-11-20 10:22:32.07651+00	182.253.63.30	\N	attendances/22/check_out/2025-11-20/082a241d-0e72-4d94-ab8d-392d6ed6f272.jpeg	2025-11-20 03:09:59.970193+00	2025-11-20 10:22:32.858333+00	-5.39300220	105.25313730	Sukamenanti, Bandar Lampung, Lampung, Sumatra, 35123, Indonesia	-5.40585980	105.25313730	Sawah Lama, Bandar Lampung, Lampung, Sumatra, 35112, Indonesia	\N
883	41	21	2025-12-09	present	2025-12-09 02:33:42.042657+00	2025-12-09 10:00:05.249118+00	7.44	41	2025-12-09 02:33:42.042657+00	103.105.82.245	\N	attendances/41/check_in/2025-12-09/7e0ff218-9b6f-4406-b35c-b845b8380882.jpeg	2025-12-09 10:00:05.249118+00	103.105.82.245	\N	attendances/41/check_out/2025-12-09/2c48bfc1-17ae-43da-ba9d-c8c53e86a6b4.jpeg	2025-12-09 02:33:43.150418+00	2025-12-09 10:00:06.285527+00	-5.38758396	105.28017995	Jalan Alam Cantik, Kalibalau Kencana, Bandar Lampung, Lampung, Sumatra, 35133, Indonesia	-5.38758520	105.28015920	Jalan Alam Kurnia, Kalibalau Kencana, Bandar Lampung, Lampung, Sumatra, 35133, Indonesia	0.00
881	22	33	2025-12-09	invalid	2025-12-09 02:16:11.981272+00	\N	\N	22	2025-12-09 02:16:11.981272+00	103.105.82.245	\N	attendances/22/check_in/2025-12-09/d2d8c77f-0fc3-4b66-ba24-9f5bc55c7eae.jpeg	\N	\N	\N	\N	2025-12-09 02:16:13.009305+00	2025-12-09 16:30:00.012144+00	-5.38757310	105.28015350	Jalan Alam Cantik, Kalibalau Kencana, Bandar Lampung, Lampung, Sumatra, 35133, Indonesia	\N	\N	\N	\N
981	58	27	2025-12-12	present	2025-12-12 01:30:57.626597+00	2025-12-12 09:31:15.895141+00	8.01	58	2025-12-12 01:30:57.626597+00	114.125.234.21	\N	attendances/58/check_in/2025-12-12/5d45d332-422e-4954-8268-52d9037a8d28.jpeg	2025-12-12 09:31:15.895141+00	180.242.4.250	\N	attendances/58/check_out/2025-12-12/cbd1ba85-9da5-4bd3-a120-bd373da92117.jpeg	2025-12-12 01:30:58.563859+00	2025-12-12 09:31:16.955195+00	-4.06641810	103.31880030	Dempo Tengah, Pagar Alam, Sumatera Selatan, Sumatra, Indonesia	-4.05607220	103.29807200	Rantau Unji, Dempo Tengah, Pagar Alam, Sumatera Selatan, Sumatra, Indonesia	0.00
985	53	25	2025-12-12	present	2025-12-12 01:59:58.494836+00	2025-12-12 09:54:29.50376+00	7.91	53	2025-12-12 01:59:58.494836+00	114.10.100.68	\N	attendances/53/check_in/2025-12-12/d3079fdf-4607-4a91-9e63-a15d2bc0c46f.jpeg	2025-12-12 09:54:29.50376+00	103.87.231.107	\N	attendances/53/check_out/2025-12-12/6e293ed9-38a4-4b26-881a-51f02e8afff0.jpeg	2025-12-12 01:59:59.262499+00	2025-12-12 09:54:30.626124+00	-5.02811880	104.30406410	Jalan Raya Serengit, Mekar Sari, Lampung Barat, Lampung, Sumatra, Indonesia	-5.02822990	104.30404580	Jalan Raya Serengit, Mekar Sari, Lampung Barat, Lampung, Sumatra, Indonesia	0.00
991	40	28	2025-12-12	present	2025-12-12 02:41:41.980386+00	2025-12-12 10:08:54.698344+00	7.45	40	2025-12-12 02:41:41.980386+00	103.105.82.245	\N	attendances/40/check_in/2025-12-12/fbc6c33b-2d66-4f94-8c1b-cadcc58a580d.jpeg	2025-12-12 10:08:54.698344+00	103.105.82.243	\N	attendances/40/check_out/2025-12-12/5188f886-07d9-4917-bd8d-5a9a0b3649b4.jpeg	2025-12-12 02:41:42.783596+00	2025-12-12 10:08:55.451889+00	-5.38759446	105.28016593	Jalan Alam Kurnia, Kalibalau Kencana, Bandar Lampung, Lampung, Sumatra, 35133, Indonesia	-5.38759446	105.28016593	Jalan Alam Kurnia, Kalibalau Kencana, Bandar Lampung, Lampung, Sumatra, 35133, Indonesia	0.00
996	59	29	2025-12-12	absent	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	2025-12-12 16:00:00.137282+00	2025-12-12 16:00:00.137286+00	\N	\N	\N	\N	\N	\N	\N
1001	14	28	2025-12-12	absent	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	2025-12-12 16:00:00.18158+00	2025-12-12 16:00:00.181583+00	\N	\N	\N	\N	\N	\N	\N
987	22	33	2025-12-12	invalid	2025-12-12 02:18:33.223916+00	\N	\N	22	2025-12-12 02:18:33.223916+00	103.105.82.245	\N	attendances/22/check_in/2025-12-12/4afaf995-166f-4236-83f3-f60c43be39e0.jpeg	\N	\N	\N	\N	2025-12-12 02:18:34.297171+00	2025-12-12 16:30:00.066361+00	-5.39283020	105.26996230	Jagabaya II, Bandar Lampung, Lampung, Sumatra, 35136, Indonesia	\N	\N	\N	\N
341	15	12	2025-11-19	invalid	2025-11-19 04:36:38.729427+00	\N	\N	15	2025-11-19 04:36:38.729427+00	182.253.63.14	Wfh lupa check in	attendances/15/check_in/2025-11-19/fb6139de-42bf-4632-b5fb-a5d4142f7b50.jpeg	\N	\N	\N	\N	2025-11-19 04:36:40.036158+00	2025-11-19 16:59:00.031731+00	-5.39571620	105.32380530	Lampung Selatan, Lampung, Sumatra, 35131, Indonesia	\N	\N	\N	\N
363	42	11	2025-11-20	present	2025-11-20 02:14:19.029508+00	2025-11-20 10:08:47.733583+00	7.91	42	2025-11-20 02:14:19.029508+00	182.253.63.30	\N	attendances/42/check_in/2025-11-20/63e80d80-0eb1-45c6-a392-efe63a921679.jpeg	2025-11-20 10:08:47.733583+00	182.253.63.30	\N	attendances/42/check_out/2025-11-20/b9a030c0-a7d0-4216-85ef-bb82b05790b0.jpeg	2025-11-20 02:14:20.686717+00	2025-11-20 10:08:48.870406+00	-5.38758060	105.28016450	Jalan Alam Cantik, Kalibalau Kencana, Bandar Lampung, Lampung, Sumatra, 35133, Indonesia	-5.38757380	105.28014170	Jalan Alam Kurnia, Kalibalau Kencana, Bandar Lampung, Lampung, Sumatra, 35133, Indonesia	\N
366	14	11	2025-11-20	invalid	2025-11-20 02:20:34.327521+00	\N	\N	14	2025-11-20 02:20:34.327521+00	182.253.63.30	\N	attendances/14/check_in/2025-11-20/8760708d-267f-4715-98a2-dd95f56b8756.jpeg	\N	\N	\N	\N	2025-11-20 02:20:35.378541+00	2025-11-20 16:59:00.029846+00	-5.39510060	105.27800960	Jalan Pulau Morotai, Kalibalau Kencana, Bandar Lampung, Lampung, Sumatra, 35133, Indonesia	\N	\N	\N	\N
882	42	28	2025-12-09	present	2025-12-09 02:25:59.994192+00	2025-12-09 09:59:04.841208+00	7.55	42	2025-12-09 02:25:59.994192+00	103.105.82.245	\N	attendances/42/check_in/2025-12-09/a8193b21-a964-4e84-b8d0-ed001a0009c0.jpeg	2025-12-09 09:59:04.841208+00	103.105.82.245	\N	attendances/42/check_out/2025-12-09/cf4acd39-809d-4ae1-9069-7dffa28064bc.jpeg	2025-12-09 02:26:01.037207+00	2025-12-09 09:59:05.869677+00	-5.38758400	105.28015900	Jalan Alam Kurnia, Kalibalau Kencana, Bandar Lampung, Lampung, Sumatra, 35133, Indonesia	-5.38758630	105.28015950	Jalan Alam Kurnia, Kalibalau Kencana, Bandar Lampung, Lampung, Sumatra, 35133, Indonesia	0.00
982	57	27	2025-12-12	present	2025-12-12 01:50:47.339554+00	2025-12-12 10:33:39.005624+00	8.71	57	2025-12-12 01:50:47.339554+00	140.213.185.188	\N	attendances/57/check_in/2025-12-12/11f1d270-f1cb-4347-947e-c9622a3205eb.jpeg	2025-12-12 10:33:39.005624+00	140.213.184.16	\N	attendances/57/check_out/2025-12-12/e2679979-614f-4cc1-bf06-8be54b4c190a.jpeg	2025-12-12 01:50:48.447683+00	2025-12-12 10:33:39.893587+00	-4.02406398	103.25498221	Pagar Alam Selatan, Pagar Alam, Sumatera Selatan, Sumatra, Indonesia	-4.05595799	103.29799287	Rantau Unji, Dempo Tengah, Pagar Alam, Sumatera Selatan, Sumatra, Indonesia	0.00
998	48	23	2025-12-12	absent	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	2025-12-12 16:00:00.160907+00	2025-12-12 16:00:00.160911+00	\N	\N	\N	\N	\N	\N	\N
1003	47	22	2025-12-12	absent	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	2025-12-12 16:00:00.191243+00	2025-12-12 16:00:00.191246+00	\N	\N	\N	\N	\N	\N	\N
990	20	31	2025-12-12	invalid	2025-12-12 02:37:39.874943+00	\N	\N	20	2025-12-12 02:37:39.874943+00	103.105.82.245	\N	attendances/20/check_in/2025-12-12/d39bbf16-f6e0-41d3-ac57-90b26e5c899f.jpeg	\N	\N	\N	\N	2025-12-12 02:37:40.596064+00	2025-12-12 16:30:00.067213+00	-5.38765200	105.28005200	Jalan Alam Kurnia, Kalibalau Kencana, Bandar Lampung, Lampung, Sumatra, 35133, Indonesia	\N	\N	\N	\N
361	39	17	2025-11-19	hybrid	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	2025-11-19 16:00:00.573163+00	2025-11-19 16:00:00.573167+00	\N	\N	\N	\N	\N	\N	\N
373	15	12	2025-11-20	present	2025-11-20 08:36:10.472523+00	2025-11-20 10:12:38.854554+00	1.61	15	2025-11-20 08:36:10.472523+00	182.253.63.30	Lupa check in maaf mbak ine	attendances/15/check_in/2025-11-20/a4f2ed51-3c86-4029-aab5-eab01d9c7bbb.jpeg	2025-11-20 10:12:38.854554+00	182.253.63.30	\N	attendances/15/check_out/2025-11-20/5531e576-9c89-4af6-a93e-14f6d6f3ba15.jpeg	2025-11-20 08:36:11.667552+00	2025-11-20 10:12:39.655958+00	-5.38757870	105.28016040	Jalan Alam Cantik, Kalibalau Kencana, Bandar Lampung, Lampung, Sumatra, 35133, Indonesia	-5.38757880	105.28016030	Jalan Alam Cantik, Kalibalau Kencana, Bandar Lampung, Lampung, Sumatra, 35133, Indonesia	\N
364	24	15	2025-11-20	present	2025-11-20 02:16:34.114936+00	2025-11-20 10:13:20.450692+00	7.95	24	2025-11-20 02:16:34.114936+00	182.253.63.30	\N	attendances/24/check_in/2025-11-20/d3d455f2-7a27-4cb7-a558-b08d0ae1486b.jpeg	2025-11-20 10:13:20.450692+00	182.253.63.30	\N	attendances/24/check_out/2025-11-20/425b4824-b829-4f96-b94e-3491f6c3df61.jpeg	2025-11-20 02:16:34.864588+00	2025-11-20 10:13:21.175043+00	-5.40999680	105.26720000	Jalan Hayam Wuruk, Gunung Sari, Bandar Lampung, Lampung, Sumatra, 35121, Indonesia	-5.37794940	105.25313730	Jalan Harapan II, Pelita, Bandar Lampung, Lampung, Sumatra, 35142, Indonesia	\N
370	44	17	2025-11-20	present	2025-11-20 03:40:39.522958+00	2025-11-20 13:05:22.398248+00	9.41	44	2025-11-20 03:40:39.522958+00	114.10.100.27	\N	attendances/44/check_in/2025-11-20/74c47886-cd1a-4685-8553-f8ad977e1a4a.jpg	2025-11-20 13:05:22.398248+00	114.10.158.252	\N	attendances/44/check_out/2025-11-20/ccbbc418-c292-4887-b63c-067df56444eb.jpeg	2025-11-20 03:40:39.820286+00	2025-11-20 13:05:23.79922+00	\N	\N	\N	-5.07608110	119.54605300	Jalur Gerbang Kedatangan Baru, Mandai, Maros, Baji Mangngai, Sulawesi Selatan, Sulawesi, 90522, Indonesia	\N
884	40	28	2025-12-09	present	2025-12-09 02:41:21.87719+00	2025-12-09 09:52:37.657221+00	7.19	40	2025-12-09 02:41:21.87719+00	103.105.82.245	\N	attendances/40/check_in/2025-12-09/0691ea93-3bb3-4f75-9a1a-f91a8f3fd769.jpeg	2025-12-09 09:52:37.657221+00	103.105.82.245	\N	attendances/40/check_out/2025-12-09/21c5a4be-fa63-4565-bdb8-af824b9bfe8d.jpeg	2025-12-09 02:41:23.033832+00	2025-12-09 09:52:38.388849+00	-5.38759397	105.28016696	Jalan Alam Kurnia, Kalibalau Kencana, Bandar Lampung, Lampung, Sumatra, 35133, Indonesia	-5.38759397	105.28016696	Jalan Alam Kurnia, Kalibalau Kencana, Bandar Lampung, Lampung, Sumatra, 35133, Indonesia	0.00
988	42	28	2025-12-12	present	2025-12-12 02:28:19.869898+00	2025-12-12 10:08:22.222124+00	7.67	42	2025-12-12 02:28:19.869898+00	103.105.82.245	\N	attendances/42/check_in/2025-12-12/3b8d6557-6dcf-40b6-82a7-90f4896dcf17.jpeg	2025-12-12 10:08:22.222124+00	103.105.82.243	\N	attendances/42/check_out/2025-12-12/4ef85922-a869-42fa-a66c-9766b7bcb443.jpeg	2025-12-12 02:28:20.812808+00	2025-12-12 10:08:23.220671+00	-5.38758080	105.28016180	Jalan Alam Cantik, Kalibalau Kencana, Bandar Lampung, Lampung, Sumatra, 35133, Indonesia	-5.38758300	105.28015720	Jalan Alam Kurnia, Kalibalau Kencana, Bandar Lampung, Lampung, Sumatra, 35133, Indonesia	0.00
983	52	24	2025-12-12	present	2025-12-12 01:54:49.047888+00	2025-12-12 10:09:40.029482+00	8.25	52	2025-12-12 01:54:49.047888+00	114.10.100.143	\N	attendances/52/check_in/2025-12-12/d2b4b4c1-8bca-457d-af40-b5c353576fc0.jpeg	2025-12-12 10:09:40.029482+00	114.10.102.84	\N	attendances/52/check_out/2025-12-12/7e78d542-de7e-4261-a2eb-40bdaf58bdc2.jpeg	2025-12-12 01:54:49.854803+00	2025-12-12 10:09:40.786224+00	-5.02834940	104.30402460	Jalan Raya Serengit, Mekar Sari, Lampung Barat, Lampung, Sumatra, Indonesia	-5.02822960	104.30404390	Jalan Raya Serengit, Mekar Sari, Lampung Barat, Lampung, Sumatra, Indonesia	0.00
989	41	21	2025-12-12	present	2025-12-12 02:37:04.914624+00	2025-12-12 10:12:05.243497+00	7.58	41	2025-12-12 02:37:04.914624+00	103.105.82.245	\N	attendances/41/check_in/2025-12-12/0c02d3a5-faf4-47c1-921c-8deae157ba94.jpeg	2025-12-12 10:12:05.243497+00	103.105.82.243	\N	attendances/41/check_out/2025-12-12/6c554015-3e91-4e9c-97e4-bc4a466841d2.jpeg	2025-12-12 02:37:05.996214+00	2025-12-12 10:12:06.014815+00	-5.38757539	105.28018330	Jalan Alam Cantik, Kalibalau Kencana, Bandar Lampung, Lampung, Sumatra, 35133, Indonesia	-5.38757539	105.28018330	Jalan Alam Cantik, Kalibalau Kencana, Bandar Lampung, Lampung, Sumatra, 35133, Indonesia	0.00
984	23	33	2025-12-12	present	2025-12-12 01:58:59.793829+00	2025-12-12 11:28:57.718508+00	9.50	23	2025-12-12 01:58:59.793829+00	140.213.111.163	\N	attendances/23/check_in/2025-12-12/a0fe3057-f9eb-4d2c-a75d-649cd0dca4fa.jpeg	2025-12-12 11:28:57.718508+00	140.213.157.9	\N	attendances/23/check_out/2025-12-12/92fe96df-3a66-4f91-ab65-a37d9e71e285.jpeg	2025-12-12 01:59:00.891947+00	2025-12-12 11:28:58.933411+00	-5.38746772	105.28011843	Jalan Alam Cantik, Kalibalau Kencana, Bandar Lampung, Lampung, Sumatra, 35133, Indonesia	-5.38754944	105.28018278	Jalan Alam Cantik, Kalibalau Kencana, Bandar Lampung, Lampung, Sumatra, 35133, Indonesia	0.00
992	44	34	2025-12-12	present	2025-12-12 03:02:17.066141+00	2025-12-12 11:37:17.116853+00	8.58	44	2025-12-12 03:02:17.066141+00	114.10.102.243	\N	attendances/44/check_in/2025-12-12/9f0edc1f-7e50-410c-8352-55cf8f80cceb.jpeg	2025-12-12 11:37:17.116853+00	114.10.100.142	\N	attendances/44/check_out/2025-12-12/1b047700-fe35-432e-8a13-4bfab832b158.jpeg	2025-12-12 03:02:18.079162+00	2025-12-12 11:37:18.184538+00	-5.38758510	105.28015910	Jalan Alam Kurnia, Kalibalau Kencana, Bandar Lampung, Lampung, Sumatra, 35133, Indonesia	-5.38758480	105.28015870	Jalan Alam Kurnia, Kalibalau Kencana, Bandar Lampung, Lampung, Sumatra, 35133, Indonesia	0.00
999	55	27	2025-12-12	absent	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	2025-12-12 16:00:00.169584+00	2025-12-12 16:00:00.169588+00	\N	\N	\N	\N	\N	\N	\N
1004	39	32	2025-12-12	hybrid	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	2025-12-12 16:00:00.200672+00	2025-12-12 16:00:00.200676+00	\N	\N	\N	\N	\N	\N	\N
362	43	17	2025-11-19	hybrid	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	2025-11-19 16:00:00.581279+00	2025-11-19 16:00:00.581283+00	\N	\N	\N	\N	\N	\N	\N
886	39	32	2025-12-09	present	2025-12-09 03:57:57.27703+00	2025-12-09 09:51:42.030185+00	5.90	39	2025-12-09 03:57:57.27703+00	103.105.82.245	\N	attendances/39/check_in/2025-12-09/d9b7a5bd-d299-42f0-84ef-905f9b750f8c.jpeg	2025-12-09 09:51:42.030185+00	103.105.82.245	\N	attendances/39/check_out/2025-12-09/8f2f8472-9775-4113-ae41-8e8ed89c4bcf.jpeg	2025-12-09 03:57:58.324006+00	2025-12-09 09:51:43.179075+00	-5.38758400	105.28015980	Jalan Alam Cantik, Kalibalau Kencana, Bandar Lampung, Lampung, Sumatra, 35133, Indonesia	-5.38758520	105.28015720	Jalan Alam Kurnia, Kalibalau Kencana, Bandar Lampung, Lampung, Sumatra, 35133, Indonesia	0.00
993	50	23	2025-12-12	present	2025-12-12 03:09:42.133057+00	2025-12-12 13:15:51.903863+00	10.10	50	2025-12-12 03:09:42.133057+00	114.10.102.215	\N	attendances/50/check_in/2025-12-12/3d7fcad3-26b7-4e5b-9942-7bf1b252b914.jpeg	2025-12-12 13:15:51.903863+00	114.10.100.124	\N	attendances/50/check_out/2025-12-12/3e5f4109-2c3f-4810-9d64-59282c378d74.jpeg	2025-12-12 03:09:43.192816+00	2025-12-12 13:15:53.042108+00	-5.42991760	104.73409020	Gisting Bawah, Tanggamus, Lampung, Sumatra, Indonesia	-5.42870640	104.73368220	Gisting Bawah, Tanggamus, Lampung, Sumatra, Indonesia	0.00
995	46	21	2025-12-12	absent	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	2025-12-12 16:00:00.1091+00	2025-12-12 16:00:00.109106+00	\N	\N	\N	\N	\N	\N	\N
1000	56	27	2025-12-12	absent	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	2025-12-12 16:00:00.176959+00	2025-12-12 16:00:00.176964+00	\N	\N	\N	\N	\N	\N	\N
1005	43	32	2025-12-12	hybrid	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	2025-12-12 16:00:00.206664+00	2025-12-12 16:00:00.206669+00	\N	\N	\N	\N	\N	\N	\N
367	40	11	2025-11-20	present	2025-11-20 02:23:10.596925+00	2025-11-20 09:22:46.681224+00	6.99	40	2025-11-20 02:23:10.596925+00	182.253.63.30	\N	attendances/40/check_in/2025-11-20/1d29eca9-2eb1-4d30-a50e-e734d3f9820d.jpeg	2025-11-20 09:22:46.681224+00	182.253.63.30	\N	attendances/40/check_out/2025-11-20/dd710188-9352-4b91-a078-2479df134039.jpeg	2025-11-20 02:23:11.346258+00	2025-11-20 09:22:47.813755+00	-5.40585980	105.25313730	Sawah Lama, Bandar Lampung, Lampung, Sumatra, 35112, Indonesia	-5.37794940	105.25313730	Jalan Harapan II, Pelita, Bandar Lampung, Lampung, Sumatra, 35142, Indonesia	\N
371	39	17	2025-11-20	present	2025-11-20 04:33:21.645248+00	2025-11-20 09:55:35.860203+00	5.37	39	2025-11-20 04:33:21.645248+00	182.253.63.30	\N	attendances/39/check_in/2025-11-20/1c11aaf1-a738-485e-af5b-afe761f97f54.jpeg	2025-11-20 09:55:35.860203+00	182.253.63.30	\N	attendances/39/check_out/2025-11-20/f3eb60f9-85fa-4843-8f62-cb34297e21c2.jpeg	2025-11-20 04:33:22.722771+00	2025-11-20 09:55:36.63543+00	-5.38757920	105.28016100	Jalan Alam Cantik, Kalibalau Kencana, Bandar Lampung, Lampung, Sumatra, 35133, Indonesia	-5.40999680	105.26720000	Jalan Hayam Wuruk, Gunung Sari, Bandar Lampung, Lampung, Sumatra, 35121, Indonesia	\N
365	41	12	2025-11-20	invalid	2025-11-20 02:19:03.830343+00	\N	\N	41	2025-11-20 02:19:03.830343+00	182.3.100.73	\N	attendances/41/check_in/2025-11-20/a77c6ae8-3483-461f-914e-127f1c2de2e9.jpeg	\N	\N	\N	\N	2025-11-20 02:19:04.548277+00	2025-11-20 16:59:00.034083+00	-5.33896920	105.21259520	Jalan Lintas Tengah Sumatera, Hajimena, Lampung Selatan, Lampung, Sumatra, 35362, Indonesia	\N	\N	\N	\N
887	14	28	2025-12-09	present	2025-12-09 09:00:00.891264+00	2025-12-09 17:00:00.891264+00	8.00	14	2025-12-09 08:48:04.588824+00	103.105.82.245	Diubah oleh Ine Laynazka pada 10-12-2025 07:56:27 WIB	attendances/14/check_in/2025-12-09/45932db3-5f0e-4d53-9d0d-fbed8e734404.jpeg	\N	\N	Diubah oleh Ine Laynazka pada 10-12-2025 07:56:27 WIB	\N	2025-12-09 08:48:05.576074+00	2025-12-10 07:56:27.893699+00	-5.38758400	105.28015680	Jalan Alam Kurnia, Kalibalau Kencana, Bandar Lampung, Lampung, Sumatra, 35133, Indonesia	\N	\N	\N	0.00
994	62	30	2025-12-12	invalid	2025-12-12 03:16:40.275083+00	\N	\N	62	2025-12-12 03:16:40.275083+00	182.3.103.158	\N	attendances/62/check_in/2025-12-12/9f46cb40-2fe2-47b1-8662-689775ccdbd8.jpeg	\N	\N	\N	\N	2025-12-12 03:16:41.48111+00	2025-12-12 16:30:00.059579+00	-5.38758520	105.28015910	Jalan Alam Kurnia, Kalibalau Kencana, Bandar Lampung, Lampung, Sumatra, 35133, Indonesia	\N	\N	\N	\N
1017	57	27	2025-12-13	present	2025-12-13 01:52:15.53249+00	2025-12-13 10:08:15.683471+00	8.27	57	2025-12-13 01:52:15.53249+00	103.144.14.2	pagar alam	attendances/57/check_in/2025-12-13/8763c5a7-a95a-46f8-a667-5b9f6f7b14f4.jpeg	2025-12-13 10:08:15.683471+00	103.144.14.2	pagar alam	attendances/57/check_out/2025-12-13/737b225c-8f02-41c6-ad79-b335863ef410.jpeg	2025-12-13 01:52:16.45902+00	2025-12-13 10:08:16.395982+00	-4.05599237	103.29803745	Rantau Unji, Dempo Tengah, Pagar Alam, Sumatera Selatan, Sumatra, Indonesia	-4.05597426	103.29806414	Rantau Unji, Dempo Tengah, Pagar Alam, Sumatera Selatan, Sumatra, Indonesia	0.00
1014	45	21	2025-12-13	present	2025-12-13 01:32:37.533086+00	2025-12-13 10:10:08.583146+00	8.63	45	2025-12-13 01:32:37.533086+00	103.144.14.2	\N	attendances/45/check_in/2025-12-13/79cf7e89-b5a8-4af8-80b9-fcc57847e980.jpeg	2025-12-13 10:10:08.583146+00	103.144.14.2	\N	attendances/45/check_out/2025-12-13/b3534b8f-1348-410a-bd64-c1a7921c76c1.jpeg	2025-12-13 01:32:38.341591+00	2025-12-13 10:10:09.331372+00	-4.05606670	103.29806550	Rantau Unji, Dempo Tengah, Pagar Alam, Sumatera Selatan, Sumatra, Indonesia	-4.05603230	103.29810899	Rantau Unji, Dempo Tengah, Pagar Alam, Sumatera Selatan, Sumatra, Indonesia	0.00
1019	24	31	2025-12-13	present	2025-12-13 02:28:14.039746+00	2025-12-13 10:39:56.401252+00	8.20	24	2025-12-13 02:28:14.039746+00	103.105.82.243	\N	attendances/24/check_in/2025-12-13/eabb13ec-2803-463a-84b9-d7f3fbf648da.jpeg	2025-12-13 10:39:56.401252+00	103.105.82.243	\N	attendances/24/check_out/2025-12-13/89b8404f-ad34-4e35-8175-8d6314b915f1.jpeg	2025-12-13 02:28:14.986626+00	2025-12-13 10:39:57.422922+00	-5.38758500	105.28015810	Jalan Alam Kurnia, Kalibalau Kencana, Bandar Lampung, Lampung, Sumatra, 35133, Indonesia	-5.38757320	105.28013780	Jalan Alam Kurnia, Kalibalau Kencana, Bandar Lampung, Lampung, Sumatra, 35133, Indonesia	0.00
1009	23	33	2025-12-13	present	2025-12-13 01:13:50.072217+00	2025-12-13 10:40:52.913748+00	9.45	23	2025-12-13 01:13:50.072217+00	103.105.82.243	\N	attendances/23/check_in/2025-12-13/26577812-30eb-4704-b470-7581a71ef7dd.jpeg	2025-12-13 10:40:52.913748+00	103.105.82.243	\N	attendances/23/check_out/2025-12-13/654db514-70b7-4b1d-abfa-927328b1c621.jpeg	2025-12-13 01:13:51.115497+00	2025-12-13 10:40:53.749386+00	-5.38757211	105.28016787	Jalan Alam Cantik, Kalibalau Kencana, Bandar Lampung, Lampung, Sumatra, 35133, Indonesia	-5.38757220	105.28016724	Jalan Alam Cantik, Kalibalau Kencana, Bandar Lampung, Lampung, Sumatra, 35133, Indonesia	0.00
368	23	15	2025-11-20	present	2025-11-20 02:43:56.307288+00	2025-11-20 10:22:29.550265+00	7.64	23	2025-11-20 02:43:56.307288+00	182.253.63.30	\N	attendances/23/check_in/2025-11-20/26d39e89-dccf-4dd6-9f5b-f679d8712b35.jpeg	2025-11-20 10:22:29.550265+00	140.213.116.154	\N	attendances/23/check_out/2025-11-20/d2ff18fe-78c3-4e62-b04b-f85aa91ef5f4.jpeg	2025-11-20 02:43:58.405452+00	2025-11-20 10:22:30.781927+00	-5.38758881	105.28020528	Jalan Alam Cantik, Kalibalau Kencana, Bandar Lampung, Lampung, Sumatra, 35133, Indonesia	-5.38747131	105.28018008	Jalan Alam Cantik, Kalibalau Kencana, Bandar Lampung, Lampung, Sumatra, 35133, Indonesia	\N
1023	42	28	2025-12-13	present	2025-12-13 03:14:13.088654+00	2025-12-13 08:00:07.918987+00	4.77	42	2025-12-13 03:14:13.088654+00	103.105.82.243	\N	attendances/42/check_in/2025-12-13/ee4152f6-2411-43e3-acac-f737b3526cfa.jpeg	2025-12-13 08:00:07.918987+00	103.105.82.243	\N	attendances/42/check_out/2025-12-13/97ed3ecb-da97-41b8-8ff7-2f949b1e416e.jpeg	2025-12-13 03:14:13.803224+00	2025-12-13 08:00:09.735422+00	-5.38758480	105.28015870	Jalan Alam Kurnia, Kalibalau Kencana, Bandar Lampung, Lampung, Sumatra, 35133, Indonesia	-5.38758710	105.28015960	Jalan Alam Kurnia, Kalibalau Kencana, Bandar Lampung, Lampung, Sumatra, 35133, Indonesia	0.00
1011	54	25	2025-12-13	present	2025-12-13 01:19:18.495874+00	2025-12-13 09:31:29.942244+00	8.20	54	2025-12-13 01:19:18.495874+00	103.87.231.107	\N	attendances/54/check_in/2025-12-13/8d67145e-2f67-4c83-9e56-cfcfc9ca4499.jpeg	2025-12-13 09:31:29.942244+00	103.87.231.107	\N	attendances/54/check_out/2025-12-13/67116d72-03c9-473d-ba1e-d0f80a838718.jpeg	2025-12-13 01:19:19.301254+00	2025-12-13 09:31:31.110357+00	-5.02823030	104.30404680	Jalan Raya Serengit, Mekar Sari, Lampung Barat, Lampung, Sumatra, Indonesia	-5.02823130	104.30404700	Jalan Raya Serengit, Mekar Sari, Lampung Barat, Lampung, Sumatra, Indonesia	0.00
1008	49	23	2025-12-13	present	2025-12-13 01:05:49.131431+00	2025-12-13 10:09:25.321335+00	9.06	49	2025-12-13 01:05:49.131431+00	103.59.44.25	\N	attendances/49/check_in/2025-12-13/bf7b993c-cdf1-4cb6-88b0-46125c70e705.jpeg	2025-12-13 10:09:25.321335+00	103.59.44.25	\N	attendances/49/check_out/2025-12-13/3d65a23d-e16e-4f0e-8802-72c6ca81ab6b.jpeg	2025-12-13 01:05:50.437314+00	2025-12-13 10:09:25.985807+00	-5.43046450	104.73900120	Gisting Bawah, Tanggamus, Lampung, Sumatra, Indonesia	-5.43037710	104.73905940	Gisting Bawah, Tanggamus, Lampung, Sumatra, Indonesia	0.00
1006	64	24	2025-12-13	invalid	2025-12-12 22:08:53.811169+00	\N	\N	64	2025-12-12 22:08:53.811169+00	110.137.39.211	\N	attendances/64/check_in/2025-12-13/fbc0b63c-df87-41da-84c1-91ae0747afac.jpeg	\N	\N	\N	\N	2025-12-12 22:08:55.325297+00	2025-12-13 16:30:00.042029+00	-4.85927062	104.93110968	Tanjung Harapan, Lampung Utara, Lampung, Sumatra, 34511, Indonesia	\N	\N	\N	\N
386	13	10	2025-11-20	absent	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	2025-11-20 16:00:00.217381+00	2025-11-20 16:00:00.217386+00	\N	\N	\N	\N	\N	\N	\N
392	43	17	2025-11-20	hybrid	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	2025-11-20 16:00:00.257945+00	2025-11-20 16:00:00.25795+00	\N	\N	\N	\N	\N	\N	\N
393	40	11	2025-11-21	present	2025-11-21 01:15:32.337061+00	2025-11-21 09:31:03.935463+00	8.26	40	2025-11-21 01:15:32.337061+00	182.253.63.30	\N	attendances/40/check_in/2025-11-21/c1a0c76c-cdf1-4226-ae67-a3f56d3ab807.jpeg	2025-11-21 09:31:03.935463+00	103.87.231.107	Dinas ke Lampung Barat	attendances/40/check_out/2025-11-21/b3988be1-394e-4252-ac16-0915bad4e8f4.jpeg	2025-11-21 01:15:34.100538+00	2025-11-21 09:31:05.603864+00	-5.37794940	105.25313730	Jalan Harapan II, Pelita, Bandar Lampung, Lampung, Sumatra, 35142, Indonesia	-5.02827361	104.30397450	Jalan Raya Serengit, Mekar Sari, Lampung Barat, Lampung, Sumatra, Indonesia	\N
397	42	11	2025-11-21	present	2025-11-21 02:22:57.512736+00	2025-11-21 10:07:35.118459+00	7.74	42	2025-11-21 02:22:57.512736+00	182.253.63.30	\N	attendances/42/check_in/2025-11-21/7de5c5b5-d96a-46a1-a58d-de638fc3d731.jpeg	2025-11-21 10:07:35.118459+00	182.253.63.30	\N	attendances/42/check_out/2025-11-21/04ff3e40-8f45-4788-8a49-3ec1e7c31aa7.jpeg	2025-11-21 02:22:59.365654+00	2025-11-21 10:07:36.112703+00	-5.38758090	105.28016460	Jalan Alam Cantik, Kalibalau Kencana, Bandar Lampung, Lampung, Sumatra, 35133, Indonesia	-5.38766530	105.28013390	Jalan Alam Kurnia, Kalibalau Kencana, Bandar Lampung, Lampung, Sumatra, 35133, Indonesia	\N
401	20	14	2025-11-21	present	2025-11-21 04:45:18.733099+00	2025-11-21 10:15:46.604456+00	5.51	20	2025-11-21 04:45:18.733099+00	182.253.63.30	\N	attendances/20/check_in/2025-11-21/5510790c-d0f7-4eaa-aee4-16fcd8997a00.jpeg	2025-11-21 10:15:46.604456+00	182.253.63.30	\N	attendances/20/check_out/2025-11-21/9a7bdcf2-b134-4d4f-9aa1-4f4a07887ecc.jpg	2025-11-21 04:45:19.969104+00	2025-11-21 10:15:47.817573+00	-5.37694900	105.27142550	Jalan Kelapa 1, Perumnas Way Halim, Bandar Lampung, Lampung, Sumatra, 35132, Indonesia	-5.39331780	105.27800970	Jalan Mohammad Kahfi Baginda, Kalibalau Kencana, Bandar Lampung, Lampung, Sumatra, 35136, Indonesia	\N
399	22	15	2025-11-21	present	2025-11-21 02:36:06.534+00	2025-11-21 10:20:54.255071+00	7.75	22	2025-11-21 02:36:06.534+00	182.253.63.30	\N	attendances/22/check_in/2025-11-21/c990f969-a9e3-48a6-93e1-126ddf5e9708.jpeg	2025-11-21 10:20:54.255071+00	182.253.63.30	\N	attendances/22/check_out/2025-11-21/eb0e285f-32cb-4d04-8862-90f7f022a6ec.jpeg	2025-11-21 02:36:07.33789+00	2025-11-21 10:20:56.479396+00	-5.38758490	105.28015010	Jalan Alam Kurnia, Kalibalau Kencana, Bandar Lampung, Lampung, Sumatra, 35133, Indonesia	-5.38758490	105.28015010	Jalan Alam Kurnia, Kalibalau Kencana, Bandar Lampung, Lampung, Sumatra, 35133, Indonesia	\N
398	24	15	2025-11-21	present	2025-11-21 02:33:53.793872+00	2025-11-21 10:21:50.255163+00	7.80	24	2025-11-21 02:33:53.793872+00	182.253.63.30	\N	attendances/24/check_in/2025-11-21/3601ffaa-efbc-405c-b31b-6c2c5b7eee4c.jpeg	2025-11-21 10:21:50.255163+00	182.253.63.30	\N	attendances/24/check_out/2025-11-21/b710aa2a-d6f0-4f6f-9d5f-4313d36a5a19.jpeg	2025-11-21 02:33:54.818894+00	2025-11-21 10:21:51.003975+00	-5.37794940	105.25313730	Jalan Harapan II, Pelita, Bandar Lampung, Lampung, Sumatra, 35142, Indonesia	-5.39331780	105.27800970	Jalan Mohammad Kahfi Baginda, Kalibalau Kencana, Bandar Lampung, Lampung, Sumatra, 35136, Indonesia	\N
400	23	15	2025-11-21	present	2025-11-21 02:42:30.762705+00	2025-11-21 10:24:46.335058+00	7.70	23	2025-11-21 02:42:30.762705+00	140.213.157.75	\N	attendances/23/check_in/2025-11-21/2802587b-be56-47bc-93a4-dfb49e08074d.jpeg	2025-11-21 10:24:46.335058+00	140.213.156.183	\N	attendances/23/check_out/2025-11-21/30cd00a5-a00a-4953-bb5d-8163efd019aa.jpeg	2025-11-21 02:42:31.863371+00	2025-11-21 10:24:47.104271+00	-5.38754204	105.28017619	Jalan Alam Cantik, Kalibalau Kencana, Bandar Lampung, Lampung, Sumatra, 35133, Indonesia	-5.38757810	105.28016981	Jalan Alam Cantik, Kalibalau Kencana, Bandar Lampung, Lampung, Sumatra, 35133, Indonesia	\N
403	14	11	2025-11-21	present	2025-11-21 11:31:08.496846+00	2025-11-21 11:31:18.884793+00	0.00	14	2025-11-21 11:31:08.496846+00	182.1.233.25	\N	attendances/14/check_in/2025-11-21/f1694476-ae6c-4bd4-9110-74cea231ef14.jpeg	2025-11-21 11:31:18.884793+00	182.1.233.25	\N	attendances/14/check_out/2025-11-21/9852c67b-6d25-4a96-9521-2e186a428189.jpeg	2025-11-21 11:31:09.487716+00	2025-11-21 11:31:19.599278+00	-5.02823980	104.30406180	Jalan Raya Serengit, Mekar Sari, Lampung Barat, Lampung, Sumatra, Indonesia	-5.02823980	104.30406180	Jalan Raya Serengit, Mekar Sari, Lampung Barat, Lampung, Sumatra, Indonesia	\N
396	15	12	2025-11-21	present	2025-11-21 02:21:19.935822+00	2025-11-21 13:58:22.278512+00	11.62	15	2025-11-21 02:21:19.935822+00	182.3.102.168	\N	attendances/15/check_in/2025-11-21/75cab032-7259-4c88-8134-7d034662911a.jpeg	2025-11-21 13:58:22.278512+00	103.87.231.107	\N	attendances/15/check_out/2025-11-21/a7225700-265b-4394-ad3a-591463d28718.jpeg	2025-11-21 02:21:20.981416+00	2025-11-21 13:58:23.610518+00	-5.38757870	105.28016020	Jalan Alam Cantik, Kalibalau Kencana, Bandar Lampung, Lampung, Sumatra, 35133, Indonesia	-5.02823430	104.30406120	Jalan Raya Serengit, Mekar Sari, Lampung Barat, Lampung, Sumatra, Indonesia	\N
402	39	17	2025-11-21	present	2025-11-21 05:21:50.000525+00	2025-11-21 15:13:59.572031+00	9.87	39	2025-11-21 05:21:50.000525+00	182.253.63.30	\N	attendances/39/check_in/2025-11-21/15a4955f-0e99-45cd-ab20-5bb75900ee28.jpeg	2025-11-21 15:13:59.572031+00	114.10.102.196	\N	attendances/39/check_out/2025-11-21/e53b792d-6c41-42f8-b869-a63b8e3a5b4d.jpeg	2025-11-21 05:21:51.019476+00	2025-11-21 15:14:00.90573+00	-5.38757920	105.28016080	Jalan Alam Cantik, Kalibalau Kencana, Bandar Lampung, Lampung, Sumatra, 35133, Indonesia	-5.44117730	105.29601690	Jalan Perumahan Garuntang Lestari, Way Lunik, Bandar Lampung, Lampung, Sumatra, 35245, Indonesia	\N
1020	40	28	2025-12-13	present	2025-12-13 02:33:01.16431+00	2025-12-13 08:03:48.84115+00	5.51	40	2025-12-13 02:33:01.16431+00	103.105.82.243	\N	attendances/40/check_in/2025-12-13/ee9019be-b7dc-4de3-9470-f4afacdd5b37.jpeg	2025-12-13 08:03:48.84115+00	103.105.82.243	\N	attendances/40/check_out/2025-12-13/4a6f78a9-4e9b-4ae4-87d6-776eebf2331b.jpeg	2025-12-13 02:33:01.928737+00	2025-12-13 08:03:49.529175+00	-5.37697930	105.27800970	Nasi Uduk Tante, Perumnas Way Halim, Harapan Jaya, Bandar Lampung, Lampung, Sumatra, 35133, Indonesia	-5.39156250	105.26996230	Jagabaya II, Bandar Lampung, Lampung, Sumatra, 35136, Indonesia	0.00
1010	58	27	2025-12-13	present	2025-12-13 01:15:57.213493+00	2025-12-13 09:49:54.936585+00	8.57	58	2025-12-13 01:15:57.213493+00	114.125.252.155	\N	attendances/58/check_in/2025-12-13/40a4d837-7b2d-429c-a81c-077729941704.jpeg	2025-12-13 09:49:54.936585+00	103.144.14.2	\N	attendances/58/check_out/2025-12-13/9a2cf9a2-16df-4ada-9190-cf2c53087171.jpeg	2025-12-13 01:15:58.227172+00	2025-12-13 09:49:55.641578+00	-4.07508320	103.30349600	Dempo Tengah, Pagar Alam, Sumatera Selatan, Sumatra, Indonesia	-4.05603920	103.29807420	Rantau Unji, Dempo Tengah, Pagar Alam, Sumatera Selatan, Sumatra, Indonesia	0.00
1024	50	23	2025-12-13	invalid	2025-12-13 03:38:33.50276+00	\N	\N	50	2025-12-13 03:38:33.50276+00	114.10.102.144	\N	attendances/50/check_in/2025-12-13/7e439219-c3b1-4977-8998-27c72c92ce2e.jpeg	\N	\N	\N	\N	2025-12-13 03:38:34.643033+00	2025-12-13 16:30:00.045304+00	-5.42507320	104.73975780	Kota Dalam, Tanggamus, Lampung, Sumatra, Indonesia	\N	\N	\N	\N
430	15	12	2025-11-22	invalid	2025-11-22 09:06:25.498513+00	\N	\N	15	2025-11-22 09:06:25.498513+00	182.3.105.72	\N	attendances/15/check_in/2025-11-22/64a57c8d-dd76-42a6-8f9a-8102eca99cdf.jpeg	\N	\N	\N	\N	2025-11-22 09:06:27.025667+00	2025-11-22 16:59:00.034468+00	-4.86099370	104.57282690	Bukit Kemuning, Lampung Utara, Lampung, Sumatra, Indonesia	\N	\N	\N	\N
394	41	12	2025-11-21	invalid	2025-11-21 01:34:40.387848+00	\N	\N	41	2025-11-21 01:34:40.387848+00	114.125.216.136	\N	attendances/41/check_in/2025-11-21/99a2c557-950f-464c-ade1-3d44c40a6702.jpeg	\N	\N	\N	\N	2025-11-21 01:34:41.397903+00	2025-11-21 16:59:00.028096+00	-5.16880880	119.43247920	Claro Hotel & Convention, Jalan Andi Djemma, Mannuruki, Tamalate, Makassar, Sulawesi Selatan, Sulawesi, 90221, Indonesia	\N	\N	\N	\N
395	44	17	2025-11-21	invalid	2025-11-21 02:12:38.692035+00	\N	\N	44	2025-11-21 02:12:38.692035+00	114.10.135.156	\N	attendances/44/check_in/2025-11-21/f0ea1376-4341-466d-967f-61362a557e80.jpeg	\N	\N	\N	\N	2025-11-21 02:12:39.792382+00	2025-11-21 16:59:00.031926+00	-5.16877030	119.43241020	Claro Hotel & Convention, Jalan Bonto Sunggu, Mannuruki, Tamalate, Makassar, Sulawesi Selatan, Sulawesi, 90223, Indonesia	\N	\N	\N	\N
1022	41	21	2025-12-13	present	2025-12-13 03:14:06.165685+00	2025-12-13 08:08:04.303608+00	4.90	41	2025-12-13 03:14:06.165685+00	103.105.82.243	\N	attendances/41/check_in/2025-12-13/1bebbf03-319d-46c8-bced-6e85c39a682f.jpeg	2025-12-13 08:08:04.303608+00	103.105.82.243	\N	attendances/41/check_out/2025-12-13/647d83a8-7973-4a39-b281-36828a6e61d3.jpeg	2025-12-13 03:14:07.146028+00	2025-12-13 08:08:05.372235+00	-5.38757562	105.28016278	Jalan Alam Cantik, Kalibalau Kencana, Bandar Lampung, Lampung, Sumatra, 35133, Indonesia	-5.38757583	105.28018637	Jalan Alam Cantik, Kalibalau Kencana, Bandar Lampung, Lampung, Sumatra, 35133, Indonesia	0.00
445	14	11	2025-11-22	absent	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	2025-11-22 16:00:01.569682+00	2025-11-22 16:00:01.569687+00	\N	\N	\N	\N	\N	\N	\N
451	39	17	2025-11-22	hybrid	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	2025-11-22 16:00:02.216105+00	2025-11-22 16:00:02.216112+00	\N	\N	\N	\N	\N	\N	\N
425	42	11	2025-11-22	invalid	2025-11-22 02:35:41.315626+00	\N	\N	42	2025-11-22 02:35:41.315626+00	182.253.63.30	\N	attendances/42/check_in/2025-11-22/c2124ec6-c037-4936-932f-dbe29895176e.jpeg	\N	\N	\N	\N	2025-11-22 02:35:42.395297+00	2025-11-22 16:59:00.037461+00	-5.38760400	105.28015120	Jalan Alam Kurnia, Kalibalau Kencana, Bandar Lampung, Lampung, Sumatra, 35133, Indonesia	\N	\N	\N	\N
1025	39	32	2025-12-13	present	2025-12-13 08:40:53.599002+00	2025-12-13 08:40:59.321378+00	0.00	39	2025-12-13 08:40:53.599002+00	103.105.82.243	\N	attendances/39/check_in/2025-12-13/5b54ed15-b663-496d-a04e-b6c08b67aec8.jpeg	2025-12-13 08:40:59.321378+00	103.105.82.243	\N	attendances/39/check_out/2025-12-13/0236257a-20f3-4289-b6ac-3263a556d19c.jpeg	2025-12-13 08:40:54.594573+00	2025-12-13 08:41:00.02957+00	-5.38759570	105.28015630	Jalan Alam Kurnia, Kalibalau Kencana, Bandar Lampung, Lampung, Sumatra, 35133, Indonesia	-5.38759570	105.28015630	Jalan Alam Kurnia, Kalibalau Kencana, Bandar Lampung, Lampung, Sumatra, 35133, Indonesia	0.00
1013	51	23	2025-12-13	present	2025-12-13 01:29:58.385348+00	2025-12-13 10:13:02.55101+00	8.72	51	2025-12-13 01:29:58.385348+00	103.59.44.25	\N	attendances/51/check_in/2025-12-13/ea659861-4f7d-423a-90d7-ed0365093296.jpeg	2025-12-13 10:13:02.55101+00	103.59.44.25	\N	attendances/51/check_out/2025-12-13/ffb7b469-24c0-4ab5-8010-a64239fa971b.jpeg	2025-12-13 01:29:59.38475+00	2025-12-13 10:13:03.511481+00	-5.43029830	104.73883670	Gisting Bawah, Tanggamus, Lampung, Sumatra, Indonesia	-5.43050200	104.73905200	Gisting Bawah, Tanggamus, Lampung, Sumatra, Indonesia	0.00
1012	63	25	2025-12-13	invalid	2025-12-13 01:23:41.67031+00	\N	\N	63	2025-12-13 01:23:41.67031+00	103.87.231.107	\N	attendances/63/check_in/2025-12-13/b6af7447-2d06-41e9-a42c-0a9c8e520527.jpeg	\N	\N	\N	\N	2025-12-13 01:23:42.738178+00	2025-12-13 16:30:00.046191+00	-5.02823020	104.30404540	Jalan Raya Serengit, Mekar Sari, Lampung Barat, Lampung, Sumatra, Indonesia	\N	\N	\N	\N
1016	53	25	2025-12-13	present	2025-12-13 01:47:13.735518+00	2025-12-13 09:31:47.485323+00	7.74	53	2025-12-13 01:47:13.735518+00	114.10.100.49	\N	attendances/53/check_in/2025-12-13/2c7b55b5-09ec-4ec9-8e26-fc54f24de07b.jpeg	2025-12-13 09:31:47.485323+00	114.10.100.49	\N	attendances/53/check_out/2025-12-13/e90986dd-9311-4d2d-87c2-85bcc3a8e167.jpeg	2025-12-13 01:47:14.449686+00	2025-12-13 09:31:48.256601+00	-5.02814120	104.30405630	Jalan Raya Serengit, Mekar Sari, Lampung Barat, Lampung, Sumatra, Indonesia	-5.02836170	104.30402560	Jalan Raya Serengit, Mekar Sari, Lampung Barat, Lampung, Sumatra, Indonesia	0.00
1015	60	29	2025-12-13	present	2025-12-13 01:44:37.981342+00	2025-12-13 11:09:22.008385+00	9.41	60	2025-12-13 01:44:37.981342+00	103.145.34.18	\N	attendances/60/check_in/2025-12-13/3a8df2c8-75f0-40b8-895c-017f78ac5d29.jpeg	2025-12-13 11:09:22.008385+00	103.145.34.18	\N	attendances/60/check_out/2025-12-13/cc2dfd0b-991e-465f-97de-6e6d03e66dca.jpeg	2025-12-13 01:44:38.956767+00	2025-12-13 11:09:22.946663+00	-5.42568860	104.73794300	Kota Dalam, Tanggamus, Lampung, Sumatra, Indonesia	-5.42568720	104.73794620	Kota Dalam, Tanggamus, Lampung, Sumatra, Indonesia	0.00
452	43	17	2025-11-22	hybrid	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	2025-11-22 16:00:02.503373+00	2025-11-22 16:00:02.503378+00	\N	\N	\N	\N	\N	\N	\N
1018	44	34	2025-12-13	present	2025-12-13 02:19:51.75882+00	2025-12-13 15:09:57.872513+00	12.84	44	2025-12-13 02:19:51.75882+00	182.3.100.161	\N	attendances/44/check_in/2025-12-13/db436746-73bf-4275-8160-167733bef9f7.jpeg	2025-12-13 15:09:57.872513+00	114.10.102.158	\N	attendances/44/check_out/2025-12-13/8f0e3696-52db-4894-b0ff-7d42ea0e7164.jpeg	2025-12-13 02:19:52.738727+00	2025-12-13 15:09:59.324025+00	-5.36166670	105.24343610	Universitas Lampung UNILA, Jalan Teknik 7, Labuhan Ratu, Bandar Lampung, Lampung, Sumatra, 35141, Indonesia	-5.37285740	105.24954240	Gang Zakaria III, Sepang Jaya, Bandar Lampung, Lampung, Sumatra, 35148, Indonesia	0.00
416	13	10	2025-11-21	absent	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	2025-11-21 16:00:00.482672+00	2025-11-21 16:00:00.482676+00	\N	\N	\N	\N	\N	\N	\N
422	43	17	2025-11-21	hybrid	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	2025-11-21 16:00:00.515465+00	2025-11-21 16:00:00.515469+00	\N	\N	\N	\N	\N	\N	\N
1007	61	29	2025-12-13	present	2025-12-12 22:49:31.02603+00	2025-12-13 09:47:37.3482+00	10.97	61	2025-12-12 22:49:31.02603+00	114.10.100.207	Pengambilan sjlam bibit kopi	attendances/61/check_in/2025-12-13/222db499-d624-474e-8a56-d509cb3b7086.jpeg	2025-12-13 09:47:37.3482+00	114.10.100.183	Pengukuran lahan timbul manabar atas	attendances/61/check_out/2025-12-13/6e016548-ad5b-4a1b-9698-253442172bc7.jpeg	2025-12-12 22:49:31.996584+00	2025-12-13 09:47:38.437623+00	-5.03110830	104.05134170	Lampung Barat, Lampung, Sumatra, 34812, Indonesia	-5.06713830	104.13079670	Lampung Barat, Lampung, Sumatra, Indonesia	0.00
1026	52	24	2025-12-13	present	2025-12-13 09:33:40.407504+00	2025-12-13 10:07:29.502188+00	0.56	52	2025-12-13 09:33:40.407504+00	114.10.100.235	Lupa foto absen pagi	attendances/52/check_in/2025-12-13/a27410a6-cfde-4d10-b579-8121b0e87471.jpeg	2025-12-13 10:07:29.502188+00	114.10.100.235	\N	attendances/52/check_out/2025-12-13/1ef9475f-23a8-4cb9-959b-ede02ca6502d.jpeg	2025-12-13 09:33:41.185986+00	2025-12-13 10:07:30.672146+00	-5.02822990	104.30404460	Jalan Raya Serengit, Mekar Sari, Lampung Barat, Lampung, Sumatra, Indonesia	-5.02823000	104.30404500	Jalan Raya Serengit, Mekar Sari, Lampung Barat, Lampung, Sumatra, Indonesia	0.00
423	40	11	2025-11-22	present	2025-11-22 00:15:55.021862+00	2025-11-22 16:01:48.97768+00	15.76	40	2025-11-22 00:15:55.021862+00	103.87.231.107	\N	attendances/40/check_in/2025-11-22/8ccb3d72-7bd2-418a-8946-c5354698315c.jpeg	2025-11-22 16:01:48.97768+00	182.253.63.28	Dinas Lampung barat 	attendances/40/check_out/2025-11-22/348736c2-7bd4-499a-9fb6-d8916b8ec2f8.jpeg	2025-11-22 00:15:56.433036+00	2025-11-22 16:01:52.310334+00	-5.02828454	104.30398676	Jalan Raya Serengit, Mekar Sari, Lampung Barat, Lampung, Sumatra, Indonesia	-5.38758716	105.28016708	Jalan Alam Cantik, Kalibalau Kencana, Bandar Lampung, Lampung, Sumatra, 35133, Indonesia	\N
429	41	12	2025-11-22	invalid	2025-11-22 05:04:04.36242+00	\N	\N	41	2025-11-22 05:04:04.36242+00	222.124.178.210	\N	attendances/41/check_in/2025-11-22/d2af7536-6097-4f0c-af8a-8291cf636265.jpeg	\N	\N	\N	\N	2025-11-22 05:04:05.195132+00	2025-11-22 16:59:00.038115+00	-5.16881890	119.43254420	Claro Hotel & Convention, Jalan Andi Djemma, Mannuruki, Tamalate, Makassar, Sulawesi Selatan, Sulawesi, 90221, Indonesia	\N	\N	\N	\N
1027	46	21	2025-12-13	absent	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	2025-12-13 16:00:00.085672+00	2025-12-13 16:00:00.085677+00	\N	\N	\N	\N	\N	\N	\N
1032	56	27	2025-12-13	absent	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	2025-12-13 16:00:00.204505+00	2025-12-13 16:00:00.204511+00	\N	\N	\N	\N	\N	\N	\N
1037	43	32	2025-12-13	hybrid	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	2025-12-13 16:00:00.247701+00	2025-12-13 16:00:00.247706+00	\N	\N	\N	\N	\N	\N	\N
1043	63	25	2025-12-14	present	2025-12-14 01:46:32.201173+00	2025-12-14 10:08:46.763498+00	8.37	63	2025-12-14 01:46:32.201173+00	103.87.231.107	\N	attendances/63/check_in/2025-12-14/12bfc8a2-236e-45e8-aa09-77ba0f551c54.jpeg	2025-12-14 10:08:46.763498+00	103.87.231.107	\N	attendances/63/check_out/2025-12-14/4465263a-bc67-4bd0-b61e-f9b510f20e64.jpeg	2025-12-14 01:46:33.227666+00	2025-12-14 10:08:47.463302+00	-5.02822990	104.30404460	Jalan Raya Serengit, Mekar Sari, Lampung Barat, Lampung, Sumatra, Indonesia	-5.02822960	104.30404280	Jalan Raya Serengit, Mekar Sari, Lampung Barat, Lampung, Sumatra, Indonesia	0.00
1048	46	21	2025-12-14	absent	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	2025-12-14 16:00:00.12188+00	2025-12-14 16:00:00.121886+00	\N	\N	\N	\N	\N	\N	\N
1053	55	27	2025-12-14	absent	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	2025-12-14 16:00:00.230412+00	2025-12-14 16:00:00.230416+00	\N	\N	\N	\N	\N	\N	\N
1057	60	29	2025-12-15	present	2025-12-15 01:04:05.117995+00	2025-12-15 10:19:33.722897+00	9.26	60	2025-12-15 01:04:05.117995+00	103.145.34.18	\N	attendances/60/check_in/2025-12-15/fa926bf2-42e3-43da-b90e-986bc89cb921.jpeg	2025-12-15 10:19:33.722897+00	103.145.34.18	\N	attendances/60/check_out/2025-12-15/951929c6-0768-4ffc-a56e-6ee66ef8a075.jpeg	2025-12-15 01:04:06.627122+00	2025-12-15 10:19:34.83701+00	-5.42569010	104.73795440	Kota Dalam, Tanggamus, Lampung, Sumatra, Indonesia	-5.42569010	104.73795440	Kota Dalam, Tanggamus, Lampung, Sumatra, Indonesia	0.00
1021	22	33	2025-12-13	present	2025-12-13 02:58:34.567095+00	2025-12-13 10:30:49.836218+00	7.54	22	2025-12-13 02:58:34.567095+00	103.105.82.243	\N	attendances/22/check_in/2025-12-13/7272a8d4-1fe8-4807-a2f5-e27c5be43315.jpeg	2025-12-13 10:30:49.836218+00	103.105.82.243	\N	attendances/22/check_out/2025-12-13/b55dea81-6334-45a6-9781-3b1f02726561.jpeg	2025-12-13 02:58:35.562183+00	2025-12-13 10:30:50.895148+00	-5.37697930	105.27800970	Nasi Uduk Tante, Perumnas Way Halim, Harapan Jaya, Bandar Lampung, Lampung, Sumatra, 35133, Indonesia	-5.39283020	105.26996230	Jagabaya II, Bandar Lampung, Lampung, Sumatra, 35136, Indonesia	0.00
1029	62	30	2025-12-13	absent	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	2025-12-13 16:00:00.152556+00	2025-12-13 16:00:00.15256+00	\N	\N	\N	\N	\N	\N	\N
1034	47	22	2025-12-13	absent	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	2025-12-13 16:00:00.219852+00	2025-12-13 16:00:00.219858+00	\N	\N	\N	\N	\N	\N	\N
424	24	15	2025-11-22	invalid	2025-11-22 02:20:52.802126+00	\N	\N	24	2025-11-22 02:20:52.802126+00	182.253.63.30	\N	attendances/24/check_in/2025-11-22/c77c1812-5312-41a8-9230-40f04c3b04f1.jpeg	\N	\N	\N	\N	2025-11-22 02:20:54.005315+00	2025-11-22 16:59:00.038695+00	-5.38757780	105.28016050	Jalan Alam Cantik, Kalibalau Kencana, Bandar Lampung, Lampung, Sumatra, 35133, Indonesia	\N	\N	\N	\N
1042	54	25	2025-12-14	present	2025-12-14 01:33:08.760394+00	2025-12-14 10:07:33.574207+00	8.57	54	2025-12-14 01:33:08.760394+00	103.87.231.107	\N	attendances/54/check_in/2025-12-14/51a594cc-2002-4725-bd92-7a4f56a69563.jpeg	2025-12-14 10:07:33.574207+00	103.87.231.107	\N	attendances/54/check_out/2025-12-14/78c38494-3be1-4dcf-9a1c-9aa22d16cb19.jpeg	2025-12-14 01:33:09.678821+00	2025-12-14 10:07:34.312154+00	-5.02823780	104.30404190	Jalan Raya Serengit, Mekar Sari, Lampung Barat, Lampung, Sumatra, Indonesia	-5.02823030	104.30403960	Jalan Raya Serengit, Mekar Sari, Lampung Barat, Lampung, Sumatra, Indonesia	0.00
1046	57	27	2025-12-14	present	2025-12-14 02:20:54.238624+00	2025-12-14 11:15:44.603635+00	8.91	57	2025-12-14 02:20:54.238624+00	180.242.4.50	pagar alam	attendances/57/check_in/2025-12-14/f71e7629-8eb4-482c-8234-8baf678675a4.jpeg	2025-12-14 11:15:44.603635+00	36.76.243.1	pagar alam	attendances/57/check_out/2025-12-14/ca877f92-81f1-44ea-b768-efac059e1095.jpeg	2025-12-14 02:20:55.399294+00	2025-12-14 11:15:45.723548+00	-4.05599243	103.29803764	Rantau Unji, Dempo Tengah, Pagar Alam, Sumatera Selatan, Sumatra, Indonesia	-4.02194343	103.25347494	Jalan Kombe Haji Umar, Pagar Alam Selatan, Pagar Alam, Sumatera Selatan, Sumatra, Indonesia	0.00
1050	50	23	2025-12-14	absent	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	2025-12-14 16:00:00.188548+00	2025-12-14 16:00:00.188552+00	\N	\N	\N	\N	\N	\N	\N
1055	47	22	2025-12-14	absent	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	2025-12-14 16:00:00.240002+00	2025-12-14 16:00:00.240005+00	\N	\N	\N	\N	\N	\N	\N
1028	59	29	2025-12-13	absent	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	2025-12-13 16:00:00.116882+00	2025-12-13 16:00:00.116887+00	\N	\N	\N	\N	\N	\N	\N
428	44	17	2025-11-22	present	2025-11-22 05:03:54.776325+00	2025-11-22 10:15:05.278156+00	5.19	44	2025-11-22 05:03:54.776325+00	114.10.134.170	\N	attendances/44/check_in/2025-11-22/5ead896c-5cd1-44bd-a084-de112ccd0289.jpeg	2025-11-22 10:15:05.278156+00	114.10.135.142	\N	attendances/44/check_out/2025-11-22/65177fee-b7b3-4561-be1e-a043f61f28ba.jpeg	2025-11-22 05:03:55.720638+00	2025-11-22 10:15:06.447657+00	-5.16880240	119.43247100	Claro Hotel & Convention, Jalan Andi Djemma, Mannuruki, Tamalate, Makassar, Sulawesi Selatan, Sulawesi, 90221, Indonesia	-5.16935480	119.43211210	Claro Hotel & Convention, Jalan Andi Djemma, Mannuruki, Tamalate, Makassar, Sulawesi Selatan, Sulawesi, 90221, Indonesia	\N
426	23	15	2025-11-22	present	2025-11-22 03:22:07.313793+00	2025-11-22 11:20:45.465253+00	7.98	23	2025-11-22 03:22:07.313793+00	182.253.63.30	\N	attendances/23/check_in/2025-11-22/704ea48d-e5c3-42fd-99e6-db1f5f292e69.jpeg	2025-11-22 11:20:45.465253+00	182.3.105.200	\N	attendances/23/check_out/2025-11-22/25e973a8-0398-46c0-9002-32b441d178ad.jpeg	2025-11-22 03:22:08.424587+00	2025-11-22 11:20:46.589157+00	-5.38758168	105.28020617	Jalan Alam Cantik, Kalibalau Kencana, Bandar Lampung, Lampung, Sumatra, 35133, Indonesia	-5.39002943	105.27919676	Kalibalau Kencana, Bandar Lampung, Lampung, Sumatra, 35133, Indonesia	\N
432	22	15	2025-11-22	absent	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	2025-11-22 16:00:01.144048+00	2025-11-22 16:00:01.144054+00	\N	\N	\N	\N	\N	\N	\N
1033	14	28	2025-12-13	absent	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	2025-12-13 16:00:00.210507+00	2025-12-13 16:00:00.210512+00	\N	\N	\N	\N	\N	\N	\N
444	13	10	2025-11-22	absent	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	2025-11-22 16:00:01.552566+00	2025-11-22 16:00:01.55257+00	\N	\N	\N	\N	\N	\N	\N
427	20	14	2025-11-22	invalid	2025-11-22 04:54:59.573343+00	\N	\N	20	2025-11-22 04:54:59.573343+00	182.253.63.30	\N	attendances/20/check_in/2025-11-22/c1ccbba8-e61c-4988-b8ab-9b0f54a619b0.jpeg	\N	\N	\N	\N	2025-11-22 04:55:01.119616+00	2025-11-22 16:59:00.039258+00	-5.39331780	105.27800970	Jalan Mohammad Kahfi Baginda, Kalibalau Kencana, Bandar Lampung, Lampung, Sumatra, 35136, Indonesia	\N	\N	\N	\N
1044	53	25	2025-12-14	present	2025-12-14 01:51:49.447265+00	2025-12-14 09:35:41.504017+00	7.73	53	2025-12-14 01:51:49.447265+00	114.10.102.221	\N	attendances/53/check_in/2025-12-14/bb95c47c-5733-485c-8ec1-fce078a27cce.jpeg	2025-12-14 09:35:41.504017+00	103.87.231.107	\N	attendances/53/check_out/2025-12-14/3bd14d3a-8f90-473d-b1f6-957237d3c3dd.jpeg	2025-12-14 01:51:50.507997+00	2025-12-14 09:35:42.558242+00	-5.02831370	104.30407630	Jalan Raya Serengit, Mekar Sari, Lampung Barat, Lampung, Sumatra, Indonesia	-5.02823290	104.30404700	Jalan Raya Serengit, Mekar Sari, Lampung Barat, Lampung, Sumatra, Indonesia	0.00
460	39	17	2025-11-24	present	2025-11-24 06:17:28.392538+00	2025-11-24 08:11:31.769168+00	1.90	39	2025-11-24 06:17:28.392538+00	182.253.63.28	\N	attendances/39/check_in/2025-11-24/905c0c61-9d84-4ed7-8718-c9a9e24cba5d.jpeg	2025-11-24 08:11:31.769168+00	182.253.63.28	\N	attendances/39/check_out/2025-11-24/88bc4040-e489-44e4-9872-e94896515487.jpeg	2025-11-24 06:17:29.971244+00	2025-11-24 08:11:33.108361+00	-5.38757890	105.28016040	Jalan Alam Cantik, Kalibalau Kencana, Bandar Lampung, Lampung, Sumatra, 35133, Indonesia	-5.38757890	105.28016040	Jalan Alam Cantik, Kalibalau Kencana, Bandar Lampung, Lampung, Sumatra, 35133, Indonesia	\N
1040	49	23	2025-12-14	present	2025-12-14 01:06:30.448559+00	2025-12-14 10:06:29.26451+00	9.00	49	2025-12-14 01:06:30.448559+00	103.59.44.25	\N	attendances/49/check_in/2025-12-14/29d319ba-4e08-4d9b-b4a6-3d0f7e1beced.jpeg	2025-12-14 10:06:29.26451+00	103.59.44.25	\N	attendances/49/check_out/2025-12-14/9fe79a5a-5cbd-4d29-9a3b-e8c7cf5fea24.jpeg	2025-12-14 01:06:31.273381+00	2025-12-14 10:06:30.263001+00	-5.43037480	104.73926020	Gisting Bawah, Tanggamus, Lampung, Sumatra, Indonesia	-5.43057760	104.73918390	Gisting Bawah, Tanggamus, Lampung, Sumatra, Indonesia	0.00
454	40	11	2025-11-24	present	2025-11-24 01:52:48.855544+00	2025-11-24 09:25:26.686346+00	7.54	40	2025-11-24 01:52:48.855544+00	182.253.63.28	\N	attendances/40/check_in/2025-11-24/fc66fe53-9660-4397-b479-17b82d302994.jpeg	2025-11-24 09:25:26.686346+00	182.253.63.28	\N	attendances/40/check_out/2025-11-24/1f9de10a-3046-4140-aad5-3b5c388c8e3f.jpeg	2025-11-24 01:52:49.65383+00	2025-11-24 09:25:27.853514+00	-5.38764613	105.28015609	Jalan Alam Kurnia, Kalibalau Kencana, Bandar Lampung, Lampung, Sumatra, 35133, Indonesia	-5.38758716	105.28016708	Jalan Alam Cantik, Kalibalau Kencana, Bandar Lampung, Lampung, Sumatra, 35133, Indonesia	\N
457	24	15	2025-11-24	present	2025-11-24 02:22:43.798616+00	2025-11-24 10:18:02.980893+00	7.92	24	2025-11-24 02:22:43.798616+00	182.253.63.28	\N	attendances/24/check_in/2025-11-24/04f4c961-4d38-45f8-83fd-d9f20f93088a.jpeg	2025-11-24 10:18:02.980893+00	182.253.63.28	\N	attendances/24/check_out/2025-11-24/aff9d3ff-930e-4fd6-b70c-f1ec8011a705.jpeg	2025-11-24 02:22:44.50719+00	2025-11-24 10:18:04.01535+00	-5.40344320	105.27047680	Jagabaya III, Bandar Lampung, Lampung, Sumatra, 35227, Indonesia	-5.39452060	105.27435180	Jagabaya II, Bandar Lampung, Lampung, Sumatra, 35136, Indonesia	\N
462	20	14	2025-11-24	present	2025-11-24 10:19:36.908051+00	2025-11-24 10:19:46.194732+00	0.00	20	2025-11-24 10:19:36.908051+00	182.253.63.28	\N	attendances/20/check_in/2025-11-24/e307a6f6-47aa-4a8b-9efd-f64adba69213.jpeg	2025-11-24 10:19:46.194732+00	182.253.63.28	\N	attendances/20/check_out/2025-11-24/44239cc4-09ab-41a1-9a49-829f45ce1065.jpeg	2025-11-24 10:19:37.093359+00	2025-11-24 10:19:46.328369+00	\N	\N	\N	\N	\N	\N	\N
453	23	15	2025-11-24	present	2025-11-24 01:50:57.981763+00	2025-11-24 12:02:52.575941+00	10.20	23	2025-11-24 01:50:57.981763+00	140.213.33.138	\N	attendances/23/check_in/2025-11-24/9770f2f1-d946-439f-8521-dc0d69b36baf.jpeg	2025-11-24 12:02:52.575941+00	182.3.102.16	\N	attendances/23/check_out/2025-11-24/2f9afc06-c8e7-4c9d-b107-53b2686cfccf.jpeg	2025-11-24 01:50:59.541506+00	2025-11-24 12:02:53.78471+00	-6.16562730	106.82595014	Mövenpick Hotel Jakarta City Centre, 7-18, Jalan Pecenongan, RW 03, Kebon Kelapa, Gambir, Jakarta Pusat, Daerah Khusus Ibukota Jakarta, Jawa, 10120, Indonesia	-6.16465739	106.82061569	Padang Merdeka, 5, Jalan Hayam Wuruk, RW 02, Kebon Kelapa, Gambir, Jakarta Pusat, Daerah Khusus Ibukota Jakarta, Jawa, 10120, Indonesia	\N
1052	52	24	2025-12-14	absent	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	2025-12-14 16:00:00.221485+00	2025-12-14 16:00:00.22149+00	\N	\N	\N	\N	\N	\N	\N
475	13	10	2025-11-24	absent	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	2025-11-24 16:00:00.588091+00	2025-11-24 16:00:00.588095+00	\N	\N	\N	\N	\N	\N	\N
477	15	12	2025-11-24	absent	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	2025-11-24 16:00:00.602683+00	2025-11-24 16:00:00.602688+00	\N	\N	\N	\N	\N	\N	\N
482	43	17	2025-11-24	hybrid	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	2025-11-24 16:00:00.63418+00	2025-11-24 16:00:00.634186+00	\N	\N	\N	\N	\N	\N	\N
459	44	17	2025-11-24	present	2025-11-24 03:29:37.768018+00	2025-11-24 16:37:23.48117+00	13.13	44	2025-11-24 03:29:37.768018+00	182.253.63.28	\N	attendances/44/check_in/2025-11-24/e3acc116-63a3-4b6e-851f-c87237dee607.jpeg	2025-11-24 16:37:23.48117+00	114.10.100.103	\N	attendances/44/check_out/2025-11-24/ee83ff28-b8d0-438f-a79a-f2a35710de15.jpeg	2025-11-24 03:29:38.820146+00	2025-11-24 16:37:24.866068+00	-5.38841170	105.27965670	Jalan Alam Jaya, Kalibalau Kencana, Bandar Lampung, Lampung, Sumatra, 35133, Indonesia	-5.37272910	105.24941740	Gang Zakaria III, Sepang Jaya, Bandar Lampung, Lampung, Sumatra, 35148, Indonesia	\N
455	41	12	2025-11-24	invalid	2025-11-24 02:21:49.887401+00	\N	\N	41	2025-11-24 02:21:49.887401+00	110.137.39.149	Wfh karena sakit	attendances/41/check_in/2025-11-24/40196c2e-c786-4fe7-a50b-d705aacb759c.jpeg	\N	\N	\N	\N	2025-11-24 02:21:50.937501+00	2025-11-24 16:59:00.032621+00	-5.42415620	105.26874310	Tanjung Raya, Bandar Lampung, Lampung, Sumatra, 35213, Indonesia	\N	\N	\N	\N
456	42	11	2025-11-24	invalid	2025-11-24 02:22:08.386529+00	\N	\N	42	2025-11-24 02:22:08.386529+00	182.253.63.28	\N	attendances/42/check_in/2025-11-24/faebc99e-c58a-488c-b012-1bb281b38efe.jpeg	\N	\N	\N	\N	2025-11-24 02:22:09.10427+00	2025-11-24 16:59:00.03672+00	-5.38757860	105.28016040	Jalan Alam Cantik, Kalibalau Kencana, Bandar Lampung, Lampung, Sumatra, 35133, Indonesia	\N	\N	\N	\N
458	22	15	2025-11-24	invalid	2025-11-24 02:41:17.216579+00	\N	\N	22	2025-11-24 02:41:17.216579+00	36.79.179.192	\N	attendances/22/check_in/2025-11-24/6bd1819e-b295-447d-a466-193c599c7443.jpeg	\N	\N	\N	\N	2025-11-24 02:41:18.201056+00	2025-11-24 16:59:00.038428+00	-6.15102990	106.81845680	Jalan Kebon Jeruk XIX, RW 09, Maphar, Taman Sari, Jakarta Barat, Daerah Khusus Ibukota Jakarta, Jawa, 11130, Indonesia	\N	\N	\N	\N
461	14	11	2025-11-24	invalid	2025-11-24 08:49:23.058118+00	\N	\N	14	2025-11-24 08:49:23.058118+00	182.253.63.28	\N	attendances/14/check_in/2025-11-24/4acfffc1-27d1-419a-bec6-29d11ab8f4ab.jpeg	\N	\N	\N	\N	2025-11-24 08:49:24.373085+00	2025-11-24 16:59:00.039137+00	-5.39452060	105.27435180	Jagabaya II, Bandar Lampung, Lampung, Sumatra, 35136, Indonesia	\N	\N	\N	\N
487	41	12	2025-11-25	present	2025-11-25 02:52:03.695253+00	2025-11-25 10:13:34.05775+00	7.36	41	2025-11-25 02:52:03.695253+00	182.253.63.28	\N	attendances/41/check_in/2025-11-25/63c93b9c-c1e9-4ca8-99bc-4f8490cad900.jpeg	2025-11-25 10:13:34.05775+00	182.253.63.28	\N	attendances/41/check_out/2025-11-25/c7709073-2c72-4bba-8963-885a0267c36b.jpeg	2025-11-25 02:52:04.7391+00	2025-11-25 10:13:35.330671+00	-5.38761200	105.28015250	Jalan Alam Kurnia, Kalibalau Kencana, Bandar Lampung, Lampung, Sumatra, 35133, Indonesia	-5.38757740	105.28014900	Jalan Alam Kurnia, Kalibalau Kencana, Bandar Lampung, Lampung, Sumatra, 35133, Indonesia	\N
486	40	11	2025-11-25	present	2025-11-25 02:28:39.465315+00	2025-11-25 10:13:46.542027+00	7.75	40	2025-11-25 02:28:39.465315+00	182.253.63.28	\N	attendances/40/check_in/2025-11-25/21cf829a-abc3-4487-b718-a7ab2066278d.jpeg	2025-11-25 10:13:46.542027+00	182.253.63.28	\N	attendances/40/check_out/2025-11-25/3667655a-0a33-4e85-8e68-50e9115bb340.jpeg	2025-11-25 02:28:40.573402+00	2025-11-25 10:13:47.30277+00	-5.39452060	105.27435180	Jagabaya II, Bandar Lampung, Lampung, Sumatra, 35136, Indonesia	-5.38758716	105.28016708	Jalan Alam Cantik, Kalibalau Kencana, Bandar Lampung, Lampung, Sumatra, 35133, Indonesia	\N
485	24	15	2025-11-25	present	2025-11-25 01:58:52.823129+00	2025-11-25 11:22:20.928217+00	9.39	24	2025-11-25 01:58:52.823129+00	114.10.102.77	\N	attendances/24/check_in/2025-11-25/0fec7d06-2465-4656-b932-112f50b862e5.jpeg	2025-11-25 11:22:20.928217+00	182.253.170.230	\N	attendances/24/check_out/2025-11-25/2a4cf04d-a983-4f81-b31d-5ffdb79f8955.jpeg	2025-11-25 01:58:53.901243+00	2025-11-25 11:22:22.058319+00	-5.39033600	105.26064640	Sidodadi, Bandar Lampung, Lampung, Sumatra, 35132, Indonesia	-6.14412250	106.87685300	RW 16, Sunter Agung, Tanjung Priok, Jakarta Utara, Daerah Khusus Ibukota Jakarta, Jawa, 14350, Indonesia	\N
1030	48	23	2025-12-13	absent	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	2025-12-13 16:00:00.170329+00	2025-12-13 16:00:00.170334+00	\N	\N	\N	\N	\N	\N	\N
1035	20	31	2025-12-13	absent	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	2025-12-13 16:00:00.226614+00	2025-12-13 16:00:00.22662+00	\N	\N	\N	\N	\N	\N	\N
1039	58	27	2025-12-14	present	2025-12-14 01:05:49.789644+00	2025-12-14 09:20:51.238376+00	8.25	58	2025-12-14 01:05:49.789644+00	180.242.4.50	\N	attendances/58/check_in/2025-12-14/e4aa1126-3786-407b-9590-64296eb576ea.jpeg	2025-12-14 09:20:51.238376+00	180.242.4.50	\N	attendances/58/check_out/2025-12-14/15da3f34-f9de-49a1-a84d-2b7f8250f340.jpeg	2025-12-14 01:05:50.91186+00	2025-12-14 09:20:52.646017+00	-4.05587940	103.29776400	Rantau Unji, Dempo Tengah, Pagar Alam, Sumatera Selatan, Sumatra, Indonesia	-4.05611120	103.29807580	Rantau Unji, Dempo Tengah, Pagar Alam, Sumatera Selatan, Sumatra, Indonesia	0.00
1041	51	23	2025-12-14	present	2025-12-14 01:23:34.563833+00	2025-12-14 10:10:59.74034+00	8.79	51	2025-12-14 01:23:34.563833+00	103.59.44.25	\N	attendances/51/check_in/2025-12-14/5051a67e-fafc-4735-bf8f-5c07f9097e99.jpeg	2025-12-14 10:10:59.74034+00	103.59.44.25	\N	attendances/51/check_out/2025-12-14/11ee9189-d184-48a9-aa3e-e4b6893d519e.jpeg	2025-12-14 01:23:35.581634+00	2025-12-14 10:11:00.427578+00	-5.43059170	104.73912830	Gisting Bawah, Tanggamus, Lampung, Sumatra, Indonesia	-5.43065000	104.73901000	Gisting Bawah, Tanggamus, Lampung, Sumatra, Indonesia	0.00
1049	59	29	2025-12-14	absent	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	2025-12-14 16:00:00.175041+00	2025-12-14 16:00:00.175045+00	\N	\N	\N	\N	\N	\N	\N
1054	56	27	2025-12-14	absent	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	2025-12-14 16:00:00.235296+00	2025-12-14 16:00:00.235298+00	\N	\N	\N	\N	\N	\N	\N
504	13	10	2025-11-25	absent	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	2025-11-25 16:00:00.531354+00	2025-11-25 16:00:00.531358+00	\N	\N	\N	\N	\N	\N	\N
506	15	12	2025-11-25	absent	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	2025-11-25 16:00:00.544178+00	2025-11-25 16:00:00.544181+00	\N	\N	\N	\N	\N	\N	\N
511	39	17	2025-11-25	hybrid	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	2025-11-25 16:00:00.571906+00	2025-11-25 16:00:00.57191+00	\N	\N	\N	\N	\N	\N	\N
512	43	17	2025-11-25	hybrid	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	2025-11-25 16:00:00.580271+00	2025-11-25 16:00:00.580274+00	\N	\N	\N	\N	\N	\N	\N
490	44	17	2025-11-25	present	2025-11-25 05:17:30.171123+00	2025-11-25 16:39:52.639308+00	11.37	44	2025-11-25 05:17:30.171123+00	114.10.100.103	\N	attendances/44/check_in/2025-11-25/5c95d512-845d-469c-b825-fd7ec4ed0ff4.jpeg	2025-11-25 16:39:52.639308+00	114.10.102.48	\N	attendances/44/check_out/2025-11-25/5af9adc1-a726-4376-93ef-20d40e942c8d.jpeg	2025-11-25 05:17:31.218794+00	2025-11-25 16:39:53.993614+00	-5.37272460	105.24941440	Gang Zakaria III, Sepang Jaya, Bandar Lampung, Lampung, Sumatra, 35148, Indonesia	-5.37250500	105.24932170	Gang Zakaria III, Sepang Jaya, Bandar Lampung, Lampung, Sumatra, 35148, Indonesia	\N
483	42	11	2025-11-25	invalid	2025-11-25 01:21:16.506262+00	\N	\N	42	2025-11-25 01:21:16.506262+00	182.3.102.202	\N	attendances/42/check_in/2025-11-25/72c1ad08-4630-4618-937e-95b16a3946a6.jpeg	\N	\N	\N	\N	2025-11-25 01:21:17.514851+00	2025-11-25 16:59:00.047626+00	-5.71267630	105.58721190	Jalan Trans Sumatera, Kedaton, Lampung Selatan, Lampung, Sumatra, 35513, Indonesia	\N	\N	\N	\N
484	23	15	2025-11-25	invalid	2025-11-25 01:53:52.597759+00	\N	\N	23	2025-11-25 01:53:52.597759+00	182.2.146.119	\N	attendances/23/check_in/2025-11-25/44623bd4-bb4b-4470-8b87-9f3daf0814bd.jpeg	\N	\N	\N	\N	2025-11-25 01:53:53.683663+00	2025-11-25 16:59:00.052724+00	-6.16561045	106.82597789	Mövenpick Hotel Jakarta City Centre, 7-18, Jalan Pecenongan, RW 03, Kebon Kelapa, Gambir, Jakarta Pusat, Daerah Khusus Ibukota Jakarta, Jawa, 10120, Indonesia	\N	\N	\N	\N
488	22	15	2025-11-25	invalid	2025-11-25 03:59:47.483978+00	\N	\N	22	2025-11-25 03:59:47.483978+00	36.79.179.192	\N	attendances/22/check_in/2025-11-25/77e27fde-fa93-43d4-bd3a-c4cd58bba15a.jpeg	\N	\N	\N	\N	2025-11-25 03:59:48.260751+00	2025-11-25 16:59:00.053704+00	-6.14564440	106.82964880	Rumah Sakit Husada, Jalan Mangga Besar XIII A, RW 01, Mangga Dua Selatan, Sawah Besar, Jakarta Pusat, Daerah Khusus Ibukota Jakarta, Jawa, 10730, Indonesia	\N	\N	\N	\N
489	20	14	2025-11-25	invalid	2025-11-25 04:37:18.962342+00	\N	\N	20	2025-11-25 04:37:18.962342+00	182.253.63.28	\N	attendances/20/check_in/2025-11-25/c25e9c09-944a-4bd0-ad03-db0b2577b97c.jpeg	\N	\N	\N	\N	2025-11-25 04:37:19.235318+00	2025-11-25 16:59:00.054419+00	\N	\N	\N	\N	\N	\N	\N
491	14	11	2025-11-25	invalid	2025-11-25 07:32:05.917744+00	\N	\N	14	2025-11-25 07:32:05.917744+00	182.253.63.28	\N	attendances/14/check_in/2025-11-25/ed776998-c9f0-4548-87c7-7e0a775ae732.jpeg	\N	\N	\N	\N	2025-11-25 07:32:07.52419+00	2025-11-25 16:59:00.055356+00	-5.39452060	105.27435180	Jagabaya II, Bandar Lampung, Lampung, Sumatra, 35136, Indonesia	\N	\N	\N	\N
518	23	15	2025-11-26	present	2025-11-26 05:39:56.601786+00	2025-11-26 09:56:45.223112+00	4.28	23	2025-11-26 05:39:56.601786+00	112.78.141.78	\N	attendances/23/check_in/2025-11-26/e4a8dbc1-02b3-4d1f-94a0-a7b325ed6f2f.jpeg	2025-11-26 09:56:45.223112+00	112.78.141.78	\N	attendances/23/check_out/2025-11-26/8d693910-6de1-4b9d-b0e5-b89fa4c164e2.jpeg	2025-11-26 05:39:57.34482+00	2025-11-26 09:56:45.949197+00	-6.14033386	106.88197957	Homefresh - Sunter Jaya, Jalan Danau Sunter Utara, Sunter Jaya, Tanjung Priok, Jakarta Utara, Daerah Khusus Ibukota Jakarta, Jawa, 14350, Indonesia	-6.14033386	106.88197957	Homefresh - Sunter Jaya, Jalan Danau Sunter Utara, Sunter Jaya, Tanjung Priok, Jakarta Utara, Daerah Khusus Ibukota Jakarta, Jawa, 14350, Indonesia	\N
513	14	11	2025-11-26	invalid	2025-11-26 02:16:01.17625+00	\N	\N	14	2025-11-26 02:16:01.17625+00	182.253.63.28	\N	attendances/14/check_in/2025-11-26/77676ad4-0186-4a73-88ab-98e1f1277a01.jpeg	\N	\N	\N	\N	2025-11-26 02:16:02.761071+00	2025-11-26 16:59:00.034509+00	-5.39967080	105.27435170	Jagabaya III, Bandar Lampung, Lampung, Sumatra, 35227, Indonesia	\N	\N	\N	\N
515	42	11	2025-11-26	invalid	2025-11-26 02:35:25.871873+00	\N	\N	42	2025-11-26 02:35:25.871873+00	182.253.63.28	\N	attendances/42/check_in/2025-11-26/7c480856-f1d7-456e-aa49-c986faf431cd.jpeg	\N	\N	\N	\N	2025-11-26 02:35:26.98132+00	2025-11-26 16:59:00.038846+00	-5.38757770	105.28014780	Jalan Alam Kurnia, Kalibalau Kencana, Bandar Lampung, Lampung, Sumatra, 35133, Indonesia	\N	\N	\N	\N
519	22	15	2025-11-26	present	2025-11-26 09:08:48.082529+00	2025-11-26 09:57:53.509031+00	0.82	22	2025-11-26 09:08:48.082529+00	112.78.141.78	\N	attendances/22/check_in/2025-11-26/5f5f934b-f528-4bb7-a0c2-3ef4a949d9c4.jpeg	2025-11-26 09:57:53.509031+00	112.78.141.78	\N	attendances/22/check_out/2025-11-26/22a4832b-58dd-4bf6-ba4b-5369e206bfeb.jpeg	2025-11-26 09:08:49.320109+00	2025-11-26 09:57:54.195842+00	-6.14353680	106.87832830	Jalan Agung Timur 2, Sunter Jaya, Tanjung Priok, Jakarta Utara, Daerah Khusus Ibukota Jakarta, Jawa, 14350, Indonesia	-6.14035240	106.88194220	Homefresh - Sunter Jaya, Jalan Danau Sunter Utara, Sunter Jaya, Tanjung Priok, Jakarta Utara, Daerah Khusus Ibukota Jakarta, Jawa, 14350, Indonesia	\N
1031	55	27	2025-12-13	absent	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	2025-12-13 16:00:00.185556+00	2025-12-13 16:00:00.185561+00	\N	\N	\N	\N	\N	\N	\N
1036	15	21	2025-12-13	absent	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	2025-12-13 16:00:00.23974+00	2025-12-13 16:00:00.239745+00	\N	\N	\N	\N	\N	\N	\N
1038	61	29	2025-12-14	present	2025-12-14 00:02:58.160151+00	2025-12-14 09:48:55.26621+00	9.77	61	2025-12-14 00:02:58.160151+00	114.10.100.183	\N	attendances/61/check_in/2025-12-14/8d778cdc-096e-4216-9806-b8bab8e34159.jpeg	2025-12-14 09:48:55.26621+00	114.10.102.33	\N	attendances/61/check_out/2025-12-14/329aa680-caf5-4b36-9fe2-0931d2527402.jpeg	2025-12-14 00:02:59.816763+00	2025-12-14 09:48:56.251179+00	-5.05153030	104.10760160	Gang Buntu, Liwa, Lampung Barat, Lampung, Sumatra, 34812, Indonesia	-5.05631330	104.11402000	Jalan Gerday, Lampung Barat, Lampung, Sumatra, Indonesia	0.00
1045	45	21	2025-12-14	present	2025-12-14 01:58:15.122307+00	2025-12-14 12:23:23.642867+00	10.42	45	2025-12-14 01:58:15.122307+00	180.242.4.50	\N	attendances/45/check_in/2025-12-14/a79577cc-9edb-4217-800e-df469a759d13.jpeg	2025-12-14 12:23:23.642867+00	180.242.4.50	\N	attendances/45/check_out/2025-12-14/8e0a6bf6-a2df-49f3-9ca5-ac456105680a.jpeg	2025-12-14 01:58:16.050653+00	2025-12-14 12:23:24.750003+00	-4.05607210	103.29807180	Rantau Unji, Dempo Tengah, Pagar Alam, Sumatera Selatan, Sumatra, Indonesia	-4.05604160	103.29806700	Rantau Unji, Dempo Tengah, Pagar Alam, Sumatera Selatan, Sumatra, Indonesia	0.00
1047	60	29	2025-12-14	present	2025-12-14 02:58:15.801313+00	2025-12-14 12:31:12.480091+00	9.55	60	2025-12-14 02:58:15.801313+00	114.10.102.27	\N	attendances/60/check_in/2025-12-14/36452b27-6d01-43ee-bc32-4373844e4c77.jpeg	2025-12-14 12:31:12.480091+00	114.10.100.211	\N	attendances/60/check_out/2025-12-14/58051d55-a62d-49ed-a610-a5e628572bd8.jpeg	2025-12-14 02:58:16.809742+00	2025-12-14 12:31:13.73137+00	-5.42630480	104.73718930	Gisting Bawah, Tanggamus, Lampung, Sumatra, Indonesia	-5.39908280	104.72644560	Tanggamus, Lampung, Sumatra, Indonesia	0.00
1051	48	23	2025-12-14	absent	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	2025-12-14 16:00:00.206485+00	2025-12-14 16:00:00.206489+00	\N	\N	\N	\N	\N	\N	\N
1056	64	24	2025-12-14	absent	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	2025-12-14 16:00:00.246196+00	2025-12-14 16:00:00.246199+00	\N	\N	\N	\N	\N	\N	\N
520	15	12	2025-11-26	present	2025-11-26 09:13:37.379279+00	2025-11-26 09:29:21.537148+00	0.26	15	2025-11-26 09:13:37.379279+00	182.253.63.28	\N	attendances/15/check_in/2025-11-26/aaa648d7-daef-4b07-a8b9-62cefb0fbc99.jpeg	2025-11-26 09:29:21.537148+00	182.3.105.220	\N	attendances/15/check_out/2025-11-26/d9276417-781e-43a8-b82c-7553409cb256.jpeg	2025-11-26 09:13:38.396785+00	2025-11-26 09:29:22.766665+00	-5.38766210	105.28013260	Jalan Alam Kurnia, Kalibalau Kencana, Bandar Lampung, Lampung, Sumatra, 35133, Indonesia	-5.38636320	105.27969310	Way Halim Permai, Bandar Lampung, Lampung, Sumatra, 35133, Indonesia	\N
514	40	11	2025-11-26	present	2025-11-26 02:30:23.247632+00	2025-11-26 09:42:31.351221+00	7.20	40	2025-11-26 02:30:23.247632+00	182.253.63.28	\N	attendances/40/check_in/2025-11-26/8010b050-19d2-4a1f-9865-fdcaf4bb4a51.jpeg	2025-11-26 09:42:31.351221+00	182.253.63.28	\N	attendances/40/check_out/2025-11-26/3a403e05-4855-40cd-bcd7-70e81634a0b3.jpeg	2025-11-26 02:30:24.338756+00	2025-11-26 09:42:32.497306+00	-5.38758601	105.28016716	Jalan Alam Cantik, Kalibalau Kencana, Bandar Lampung, Lampung, Sumatra, 35133, Indonesia	-5.38758601	105.28016716	Jalan Alam Cantik, Kalibalau Kencana, Bandar Lampung, Lampung, Sumatra, 35133, Indonesia	\N
517	24	15	2025-11-26	present	2025-11-26 05:39:16.931423+00	2025-11-26 09:56:21.552073+00	4.28	24	2025-11-26 05:39:16.931423+00	114.8.234.36	\N	attendances/24/check_in/2025-11-26/335c5335-4efe-47c6-a744-fdadef1203db.jpeg	2025-11-26 09:56:21.552073+00	114.4.82.251	\N	attendances/24/check_out/2025-11-26/fad7702d-35d2-4541-8eb9-bef4c9f8c01e.jpeg	2025-11-26 05:39:18.450291+00	2025-11-26 09:56:22.473726+00	-6.14036230	106.88193260	Homefresh - Sunter Jaya, Jalan Danau Sunter Utara, Sunter Jaya, Tanjung Priok, Jakarta Utara, Daerah Khusus Ibukota Jakarta, Jawa, 14350, Indonesia	-6.14036230	106.88193260	Homefresh - Sunter Jaya, Jalan Danau Sunter Utara, Sunter Jaya, Tanjung Priok, Jakarta Utara, Daerah Khusus Ibukota Jakarta, Jawa, 14350, Indonesia	\N
516	44	17	2025-11-26	present	2025-11-26 03:23:23.983992+00	2025-11-26 15:29:18.540247+00	12.10	44	2025-11-26 03:23:23.983992+00	182.253.63.28	\N	attendances/44/check_in/2025-11-26/4c53a20d-41c0-4dcd-9cad-93ea24df7b73.jpeg	2025-11-26 15:29:18.540247+00	114.10.102.215	\N	attendances/44/check_out/2025-11-26/98e35999-3f37-43fd-9443-b6478338fb16.jpeg	2025-11-26 03:23:25.00907+00	2025-11-26 15:29:20.07802+00	-5.38757910	105.28015920	Jalan Alam Cantik, Kalibalau Kencana, Bandar Lampung, Lampung, Sumatra, 35133, Indonesia	-5.37268470	105.24945360	Gang Zakaria III, Sepang Jaya, Bandar Lampung, Lampung, Sumatra, 35148, Indonesia	\N
1058	49	23	2025-12-15	present	2025-12-15 01:12:18.178195+00	2025-12-15 10:08:00.620054+00	8.93	49	2025-12-15 01:12:18.178195+00	103.59.44.25	\N	attendances/49/check_in/2025-12-15/0ef759ec-823a-4614-85b6-ab69e15003df.jpeg	2025-12-15 10:08:00.620054+00	103.59.44.25	\N	attendances/49/check_out/2025-12-15/06399860-670c-4aaf-a5a0-0a516a363f6f.jpeg	2025-12-15 01:12:19.120569+00	2025-12-15 10:08:01.659312+00	-5.43059770	104.73919130	Gisting Bawah, Tanggamus, Lampung, Sumatra, Indonesia	-5.43058890	104.73915970	Gisting Bawah, Tanggamus, Lampung, Sumatra, Indonesia	0.00
1065	45	21	2025-12-15	present	2025-12-15 01:40:52.558814+00	2025-12-15 10:45:57.71955+00	9.08	45	2025-12-15 01:40:52.558814+00	180.242.4.50	\N	attendances/45/check_in/2025-12-15/8acf9fce-55db-4b47-be8f-1a1da36316e2.jpeg	2025-12-15 10:45:57.71955+00	180.242.4.50	\N	attendances/45/check_out/2025-12-15/9d37235e-3ec4-4ddd-a5a7-4f92f9b8f2e4.jpeg	2025-12-15 01:40:53.301961+00	2025-12-15 10:45:58.767284+00	-4.05604299	103.29811906	Rantau Unji, Dempo Tengah, Pagar Alam, Sumatera Selatan, Sumatra, Indonesia	-4.05604299	103.29811906	Rantau Unji, Dempo Tengah, Pagar Alam, Sumatera Selatan, Sumatra, Indonesia	0.00
1059	64	24	2025-12-15	invalid	2025-12-15 01:15:03.388169+00	\N	\N	64	2025-12-15 01:15:03.388169+00	110.137.39.211	\N	attendances/64/check_in/2025-12-15/d89a74bd-8dae-4cd5-a46f-e6e04cf5be65.jpeg	\N	\N	\N	\N	2025-12-15 01:15:04.141083+00	2025-12-15 16:30:00.060784+00	-4.85927062	104.93110968	Tanjung Harapan, Lampung Utara, Lampung, Sumatra, 34511, Indonesia	\N	\N	\N	\N
533	13	10	2025-11-26	absent	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	2025-11-26 16:00:00.572982+00	2025-11-26 16:00:00.572985+00	\N	\N	\N	\N	\N	\N	\N
539	20	14	2025-11-26	absent	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	2025-11-26 16:00:00.598705+00	2025-11-26 16:00:00.598708+00	\N	\N	\N	\N	\N	\N	\N
540	39	17	2025-11-26	hybrid	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	2025-11-26 16:00:00.60233+00	2025-11-26 16:00:00.602332+00	\N	\N	\N	\N	\N	\N	\N
541	41	12	2025-11-26	absent	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	2025-11-26 16:00:00.607981+00	2025-11-26 16:00:00.607984+00	\N	\N	\N	\N	\N	\N	\N
542	43	17	2025-11-26	hybrid	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	2025-11-26 16:00:00.612834+00	2025-11-26 16:00:00.612837+00	\N	\N	\N	\N	\N	\N	\N
550	15	12	2025-11-27	present	2025-11-27 03:08:48.250384+00	2025-11-27 09:18:21.252055+00	6.16	15	2025-11-27 03:08:48.250384+00	182.253.63.28	\N	attendances/15/check_in/2025-11-27/6d96bf52-bbcd-461c-b284-c571c259aef6.jpeg	2025-11-27 09:18:21.252055+00	182.253.63.28	\N	attendances/15/check_out/2025-11-27/315d5dd6-c0df-4b33-b126-d0f120a4fd5b.jpeg	2025-11-27 03:08:49.754605+00	2025-11-27 09:18:22.733912+00	-5.38757850	105.28016030	Jalan Alam Cantik, Kalibalau Kencana, Bandar Lampung, Lampung, Sumatra, 35133, Indonesia	-5.38760300	105.28014880	Jalan Alam Kurnia, Kalibalau Kencana, Bandar Lampung, Lampung, Sumatra, 35133, Indonesia	\N
545	42	11	2025-11-27	present	2025-11-27 02:22:45.395599+00	2025-11-27 09:20:40.829271+00	6.97	42	2025-11-27 02:22:45.395599+00	182.253.63.28	\N	attendances/42/check_in/2025-11-27/905fb10e-d1ab-43e0-b6b5-8a824210ccf3.jpeg	2025-11-27 09:20:40.829271+00	182.253.63.28	\N	attendances/42/check_out/2025-11-27/cdb65c6c-e226-4c4b-87e2-3b628e025e47.jpeg	2025-11-27 02:22:46.185354+00	2025-11-27 09:20:41.655905+00	-5.38757860	105.28016050	Jalan Alam Cantik, Kalibalau Kencana, Bandar Lampung, Lampung, Sumatra, 35133, Indonesia	-5.38766360	105.28014120	Jalan Alam Kurnia, Kalibalau Kencana, Bandar Lampung, Lampung, Sumatra, 35133, Indonesia	\N
549	44	17	2025-11-27	present	2025-11-27 03:08:47.982973+00	2025-11-27 09:38:15.187575+00	6.49	44	2025-11-27 03:08:47.982973+00	182.253.63.28	\N	attendances/44/check_in/2025-11-27/dbcad1a8-2d88-4042-a5d7-08992f92178e.jpeg	2025-11-27 09:38:15.187575+00	182.253.63.28	\N	attendances/44/check_out/2025-11-27/69678504-bfd6-40b7-b3f2-4694f1efd16e.jpeg	2025-11-27 03:08:48.790383+00	2025-11-27 09:38:16.227005+00	-5.38757970	105.28016120	Jalan Alam Cantik, Kalibalau Kencana, Bandar Lampung, Lampung, Sumatra, 35133, Indonesia	-5.38765590	105.28013590	Jalan Alam Kurnia, Kalibalau Kencana, Bandar Lampung, Lampung, Sumatra, 35133, Indonesia	\N
547	14	11	2025-11-27	present	2025-11-27 03:08:38.024394+00	2025-11-27 10:13:59.262673+00	7.09	14	2025-11-27 03:08:38.024394+00	182.253.63.28	\N	attendances/14/check_in/2025-11-27/477d8324-b8c3-4d84-a2b7-9c8ba4864253.jpeg	2025-11-27 10:13:59.262673+00	182.3.69.35	\N	attendances/14/check_out/2025-11-27/fbeebcc0-b3ff-4fe5-8959-f37c7f0f86b2.jpeg	2025-11-27 03:08:39.17336+00	2025-11-27 10:14:01.849984+00	-5.39967080	105.27435170	Jagabaya III, Bandar Lampung, Lampung, Sumatra, 35227, Indonesia	-5.38757910	105.28011450	Jalan Alam Kurnia, Kalibalau Kencana, Bandar Lampung, Lampung, Sumatra, 35133, Indonesia	\N
553	39	17	2025-11-27	present	2025-11-27 05:38:32.577062+00	2025-11-27 10:41:17.609717+00	5.05	39	2025-11-27 05:38:32.577062+00	112.78.141.78	\N	attendances/39/check_in/2025-11-27/b2eeadf7-fd64-43f9-97ba-08909da8b6bd.jpeg	2025-11-27 10:41:17.609717+00	112.78.141.78	\N	attendances/39/check_out/2025-11-27/67413594-83b2-43c4-ad22-eb5d426d047d.jpeg	2025-11-27 05:38:34.173655+00	2025-11-27 10:41:18.684753+00	-6.14443780	106.88127880	Jalan Danau Sunter Selatan, RW 14, Sunter Jaya, Tanjung Priok, Jakarta Utara, Daerah Khusus Ibukota Jakarta, Jawa, 14350, Indonesia	-6.14037080	106.88190480	Homefresh - Sunter Jaya, Jalan Danau Sunter Utara, Sunter Jaya, Tanjung Priok, Jakarta Utara, Daerah Khusus Ibukota Jakarta, Jawa, 14350, Indonesia	\N
551	22	15	2025-11-27	present	2025-11-27 04:10:33.084878+00	2025-11-27 10:52:54.224121+00	6.71	22	2025-11-27 04:10:33.084878+00	112.78.141.78	\N	attendances/22/check_in/2025-11-27/9418a0a5-8f37-4d4e-8601-c3ddd9fb7500.jpeg	2025-11-27 10:52:54.224121+00	112.78.141.78	\N	attendances/22/check_out/2025-11-27/cf2ba44c-b80e-4c84-a0dd-6bc63362bf1e.jpeg	2025-11-27 04:10:33.957784+00	2025-11-27 10:52:55.209666+00	-6.14039540	106.88186600	Homefresh - Sunter Jaya, Jalan Danau Sunter Utara, Sunter Jaya, Tanjung Priok, Jakarta Utara, Daerah Khusus Ibukota Jakarta, Jawa, 14350, Indonesia	-6.14040240	106.88185110	Homefresh - Sunter Jaya, Jalan Danau Sunter Utara, Sunter Jaya, Tanjung Priok, Jakarta Utara, Daerah Khusus Ibukota Jakarta, Jawa, 14350, Indonesia	\N
572	43	17	2025-11-27	hybrid	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	2025-11-27 16:00:01.483653+00	2025-11-27 16:00:01.483657+00	\N	\N	\N	\N	\N	\N	\N
548	41	12	2025-11-27	present	2025-11-27 03:08:45.470621+00	2025-11-27 09:20:41.020348+00	6.20	41	2025-11-27 03:08:45.470621+00	182.253.63.28	\N	attendances/41/check_in/2025-11-27/b2aabf3d-e6a2-4c03-a367-92dac428138a.jpeg	2025-11-27 09:20:41.020348+00	182.253.63.28	\N	attendances/41/check_out/2025-11-27/e6249c0d-e77d-4d2c-892d-b139708d6e51.jpeg	2025-11-27 03:08:46.218233+00	2025-11-27 09:20:42.627588+00	-5.38758240	105.28016090	Jalan Alam Cantik, Kalibalau Kencana, Bandar Lampung, Lampung, Sumatra, 35133, Indonesia	-5.38766670	105.28013600	Jalan Alam Kurnia, Kalibalau Kencana, Bandar Lampung, Lampung, Sumatra, 35133, Indonesia	\N
1069	61	29	2025-12-15	present	2025-12-15 02:19:26.018066+00	2025-12-15 09:51:42.922938+00	7.54	61	2025-12-15 02:19:26.018066+00	114.10.100.224	\N	attendances/61/check_in/2025-12-15/79990344-3549-4ee1-bc4f-3a88c0bf6884.jpeg	2025-12-15 09:51:42.922938+00	114.10.100.224	\N	attendances/61/check_out/2025-12-15/e890caea-9d1e-4169-b1a5-59d8570e0290.jpeg	2025-12-15 02:19:26.751278+00	2025-12-15 09:51:43.984579+00	-5.06667000	104.13323500	Lampung Barat, Lampung, Sumatra, Indonesia	-5.05148500	104.10720830	Gang Bersana, Liwa, Lampung Barat, Lampung, Sumatra, 34812, Indonesia	0.00
1060	51	23	2025-12-15	present	2025-12-15 01:22:40.167831+00	2025-12-15 10:12:29.121256+00	8.83	51	2025-12-15 01:22:40.167831+00	103.59.44.25	\N	attendances/51/check_in/2025-12-15/83da6c7e-a867-4513-95b5-0d0407e37907.jpeg	2025-12-15 10:12:29.121256+00	103.59.44.25	\N	attendances/51/check_out/2025-12-15/712b5979-ac48-4d77-833c-1145a2f8da3a.jpeg	2025-12-15 01:22:41.197826+00	2025-12-15 10:12:29.858677+00	-5.43050470	104.73907430	Gisting Bawah, Tanggamus, Lampung, Sumatra, Indonesia	-5.43055170	104.73910000	Gisting Bawah, Tanggamus, Lampung, Sumatra, Indonesia	0.00
575	40	11	2025-11-28	present	2025-11-28 01:07:24.367538+00	2025-11-28 09:44:02.47169+00	8.61	40	2025-11-28 01:07:24.367538+00	182.253.63.31	Dinas Undian Tanggamus	attendances/40/check_in/2025-11-28/8094be0e-f52a-40a9-a34f-1adf8f11ee48.jpeg	2025-11-28 09:44:02.47169+00	103.59.44.25	Dinas tanggamus	attendances/40/check_out/2025-11-28/d45667b2-3a18-445e-932f-3adea7be992e.jpeg	2025-11-28 01:07:25.407428+00	2025-11-28 09:44:03.456827+00	-5.38756154	105.28016099	Jalan Alam Cantik, Kalibalau Kencana, Bandar Lampung, Lampung, Sumatra, 35133, Indonesia	-5.43293440	104.73635840	Gisting Bawah, Tanggamus, Lampung, Sumatra, Indonesia	\N
578	44	17	2025-11-28	present	2025-11-28 03:42:12.017869+00	2025-11-28 11:09:03.683811+00	7.45	44	2025-11-28 03:42:12.017869+00	182.253.63.31	\N	attendances/44/check_in/2025-11-28/af6b0896-6df0-4c7e-9b62-8ede22f1034f.jpeg	2025-11-28 11:09:03.683811+00	182.253.63.31	\N	attendances/44/check_out/2025-11-28/75f1420f-9ae4-4bdf-9b47-4ec9f02bf8e3.jpeg	2025-11-28 03:42:13.062333+00	2025-11-28 11:09:05.520727+00	-5.38762950	105.28014520	Jalan Alam Kurnia, Kalibalau Kencana, Bandar Lampung, Lampung, Sumatra, 35133, Indonesia	-5.38767330	105.28024830	Jalan Alam Cantik, Kalibalau Kencana, Bandar Lampung, Lampung, Sumatra, 35133, Indonesia	\N
581	20	14	2025-11-28	present	2025-11-28 11:10:25.059396+00	2025-11-28 11:10:40.922085+00	0.00	20	2025-11-28 11:10:25.059396+00	182.253.63.31	\N	attendances/20/check_in/2025-11-28/6957bbc9-c8eb-4548-ac3b-0857d7bb57a3.jpeg	2025-11-28 11:10:40.922085+00	182.253.63.31	Lupa absen 	attendances/20/check_out/2025-11-28/be3df0ab-4ef2-4d91-bb5d-df11baefe4d6.jpeg	2025-11-28 11:10:25.219581+00	2025-11-28 11:10:41.059695+00	\N	\N	\N	\N	\N	\N	\N
596	14	11	2025-11-28	absent	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	2025-11-28 16:00:00.592534+00	2025-11-28 16:00:00.592537+00	\N	\N	\N	\N	\N	\N	\N
546	40	11	2025-11-27	present	2025-11-27 02:29:21.922698+00	2025-11-27 10:04:58.572487+00	7.59	40	2025-11-27 02:29:21.922698+00	182.253.63.28	\N	attendances/40/check_in/2025-11-27/31762b6f-700d-43fe-8a83-c53147fe2925.jpeg	2025-11-27 10:04:58.572487+00	182.253.63.28	\N	attendances/40/check_out/2025-11-27/f699904e-f43d-4c78-8a5e-0e04d24e85c1.jpeg	2025-11-27 02:29:22.675567+00	2025-11-27 10:05:00.179735+00	-5.38758490	105.28016400	Jalan Alam Cantik, Kalibalau Kencana, Bandar Lampung, Lampung, Sumatra, 35133, Indonesia	-5.40016640	105.27703040	Jagabaya III, Bandar Lampung, Lampung, Sumatra, 35227, Indonesia	\N
574	24	15	2025-11-28	present	2025-11-28 01:02:28.125121+00	2025-11-28 08:30:42.24632+00	7.47	24	2025-11-28 01:02:28.125121+00	114.10.64.155	\N	attendances/24/check_in/2025-11-28/d5804681-bfa1-49b4-9a7c-5a130cd937b4.jpeg	2025-11-28 08:30:42.24632+00	114.10.102.86	\N	attendances/24/check_out/2025-11-28/d2da57ab-8984-487f-92aa-ddefa73810b7.jpeg	2025-11-28 01:02:28.945375+00	2025-11-28 08:30:43.67327+00	-6.20625920	106.80729600	Soto Sedaap Boyolali Hj. Widodo, 23, Jalan Pejompongan Baru, RW 05, Bendungan Hilir, Tanah Abang, Jakarta Pusat, Daerah Khusus Ibukota Jakarta, Jawa, 10210, Indonesia	-5.39033600	105.26064640	Sidodadi, Bandar Lampung, Lampung, Sumatra, 35132, Indonesia	\N
580	15	12	2025-11-28	present	2025-11-28 05:02:34.25414+00	2025-11-28 09:28:53.865267+00	4.44	15	2025-11-28 05:02:34.25414+00	182.3.103.123	\N	attendances/15/check_in/2025-11-28/5ad2f538-4ce4-427c-9fa9-92394a3bbd34.jpeg	2025-11-28 09:28:53.865267+00	182.3.103.123	\N	attendances/15/check_out/2025-11-28/39a148e1-4d03-4f40-98df-68ece4116f48.jpeg	2025-11-28 05:02:35.278655+00	2025-11-28 09:28:54.946665+00	-5.43080180	104.73885650	Gisting Bawah, Tanggamus, Lampung, Sumatra, Indonesia	-5.26934210	104.72519610	Karang Sari, Tanggamus, Lampung, Sumatra, Indonesia	\N
576	42	11	2025-11-28	present	2025-11-28 02:36:06.929541+00	2025-11-28 10:06:59.308311+00	7.51	42	2025-11-28 02:36:06.929541+00	182.253.63.31	\N	attendances/42/check_in/2025-11-28/eb37cecd-e532-4b8e-9ef3-e6a98b96ffa1.jpeg	2025-11-28 10:06:59.308311+00	182.253.63.31	\N	attendances/42/check_out/2025-11-28/5b79a906-9c2e-4f1a-a9c0-9999fd69ed07.jpeg	2025-11-28 02:36:08.079926+00	2025-11-28 10:07:00.332546+00	-5.38765040	105.28013950	Jalan Alam Kurnia, Kalibalau Kencana, Bandar Lampung, Lampung, Sumatra, 35133, Indonesia	-5.38758890	105.28015690	Jalan Alam Kurnia, Kalibalau Kencana, Bandar Lampung, Lampung, Sumatra, 35133, Indonesia	\N
577	41	12	2025-11-28	present	2025-11-28 02:57:31.434599+00	2025-11-28 11:11:18.129014+00	8.23	41	2025-11-28 02:57:31.434599+00	182.253.63.31	\N	attendances/41/check_in/2025-11-28/36f3bfc7-7cb0-4f14-b8ca-7d62496ea254.jpeg	2025-11-28 11:11:18.129014+00	182.253.63.31	\N	attendances/41/check_out/2025-11-28/b4b4ed50-8a2f-40ab-aecf-e56fe69992c7.jpeg	2025-11-28 02:57:32.407572+00	2025-11-28 11:11:21.146269+00	-5.38767000	105.28013350	Jalan Alam Kurnia, Kalibalau Kencana, Bandar Lampung, Lampung, Sumatra, 35133, Indonesia	-5.38757750	105.28015510	Jalan Alam Cantik, Kalibalau Kencana, Bandar Lampung, Lampung, Sumatra, 35133, Indonesia	\N
1068	62	30	2025-12-15	present	2025-12-15 02:19:12.667019+00	2025-12-15 10:03:22.887861+00	7.74	62	2025-12-15 02:19:12.667019+00	114.125.246.17	\N	attendances/62/check_in/2025-12-15/4dfbc5b5-7290-4f80-a22f-dadc08de96b7.jpeg	2025-12-15 10:03:22.887861+00	182.3.100.217	\N	attendances/62/check_out/2025-12-15/e17dff68-1607-4e97-a75b-fc7cd4f8d343.jpeg	2025-12-15 02:19:13.623168+00	2025-12-15 10:03:25.756617+00	-5.38270900	105.19932280	Jalan Imam Bonjol, Kurungannyawa, Pesawaran, Lampung, Sumatra, 35155, Indonesia	-5.38990110	105.20971860	Jalan Imam Bonjol, Bandar Lampung, Pesawaran, Lampung, Sumatra, 35155, Indonesia	0.00
602	43	17	2025-11-28	hybrid	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	2025-11-28 16:00:00.621931+00	2025-11-28 16:00:00.621935+00	\N	\N	\N	\N	\N	\N	\N
1064	52	24	2025-12-15	present	2025-12-15 01:38:13.227817+00	2025-12-15 10:21:16.598819+00	8.72	52	2025-12-15 01:38:13.227817+00	114.10.100.2	\N	attendances/52/check_in/2025-12-15/24abb801-a7b3-45b9-98c1-92c93bd4eeef.jpeg	2025-12-15 10:21:16.598819+00	114.10.102.155	\N	attendances/52/check_out/2025-12-15/fac60795-26be-4f3e-afc6-76882a7ec239.jpeg	2025-12-15 01:38:13.940403+00	2025-12-15 10:21:17.584736+00	-5.02810920	104.30411630	Jalan Raya Serengit, Mekar Sari, Lampung Barat, Lampung, Sumatra, Indonesia	-5.02823010	104.30404530	Jalan Raya Serengit, Mekar Sari, Lampung Barat, Lampung, Sumatra, Indonesia	0.00
1063	54	25	2025-12-15	present	2025-12-15 01:37:20.900696+00	2025-12-15 10:35:50.451547+00	8.97	54	2025-12-15 01:37:20.900696+00	103.87.231.107	\N	attendances/54/check_in/2025-12-15/c22d5a70-0291-4a8c-a598-a205aabd7be5.jpeg	2025-12-15 10:35:50.451547+00	103.87.231.107	\N	attendances/54/check_out/2025-12-15/4a6e6d5b-a633-45f5-88d6-26fc393d12fc.jpeg	2025-12-15 01:37:21.820315+00	2025-12-15 10:35:51.398819+00	-5.02822990	104.30404580	Jalan Raya Serengit, Mekar Sari, Lampung Barat, Lampung, Sumatra, Indonesia	-5.02823700	104.30403790	Jalan Raya Serengit, Mekar Sari, Lampung Barat, Lampung, Sumatra, Indonesia	0.00
1067	57	27	2025-12-15	present	2025-12-15 02:10:53.233787+00	2025-12-15 10:47:34.305893+00	8.61	57	2025-12-15 02:10:53.233787+00	180.242.4.50	pagar alam	attendances/57/check_in/2025-12-15/c83331a2-9c94-4a2f-836d-76adf7db138e.jpeg	2025-12-15 10:47:34.305893+00	140.213.185.224	\N	attendances/57/check_out/2025-12-15/685de3b0-4316-41f5-b80d-ca666426452c.jpeg	2025-12-15 02:10:54.268936+00	2025-12-15 10:47:35.074682+00	-4.05599177	103.29803793	Rantau Unji, Dempo Tengah, Pagar Alam, Sumatera Selatan, Sumatra, Indonesia	-4.05597426	103.29806414	Rantau Unji, Dempo Tengah, Pagar Alam, Sumatera Selatan, Sumatra, Indonesia	0.00
1062	63	25	2025-12-15	present	2025-12-15 01:29:05.308183+00	2025-12-15 10:49:04.389879+00	9.33	63	2025-12-15 01:29:05.308183+00	103.87.231.107	\N	attendances/63/check_in/2025-12-15/a7194ff3-0ef2-40e2-a63a-950ac4719e92.jpeg	2025-12-15 10:49:04.389879+00	103.87.231.107	\N	attendances/63/check_out/2025-12-15/689bee1e-617b-49dd-a970-2c5d1cd93699.jpeg	2025-12-15 01:29:06.281867+00	2025-12-15 10:49:05.13386+00	-5.02824420	104.30404510	Jalan Raya Serengit, Mekar Sari, Lampung Barat, Lampung, Sumatra, Indonesia	-5.02824540	104.30404560	Jalan Raya Serengit, Mekar Sari, Lampung Barat, Lampung, Sumatra, Indonesia	0.00
1071	23	33	2025-12-15	present	2025-12-15 02:21:59.707522+00	2025-12-15 11:02:59.386603+00	8.68	23	2025-12-15 02:21:59.707522+00	103.105.82.243	\N	attendances/23/check_in/2025-12-15/a67100d9-b527-414b-813b-16048f9301b6.jpeg	2025-12-15 11:02:59.386603+00	103.105.82.243	\N	attendances/23/check_out/2025-12-15/bde028a1-a125-4bdb-b98c-e60507fc55bc.jpeg	2025-12-15 02:22:00.480067+00	2025-12-15 11:03:00.202259+00	-5.38754991	105.28018388	Jalan Alam Cantik, Kalibalau Kencana, Bandar Lampung, Lampung, Sumatra, 35133, Indonesia	-5.38754991	105.28018388	Jalan Alam Cantik, Kalibalau Kencana, Bandar Lampung, Lampung, Sumatra, 35133, Indonesia	0.00
544	24	15	2025-11-27	present	2025-11-27 02:20:54.148832+00	2025-11-27 10:18:09.09148+00	7.95	24	2025-11-27 02:20:54.148832+00	114.10.29.3	\N	attendances/24/check_in/2025-11-27/ea30f4c9-e14c-4659-8940-44f7a9e888f4.jpeg	2025-11-27 10:18:09.09148+00	114.10.29.3	\N	attendances/24/check_out/2025-11-27/3bc4e3ba-7c01-44c6-a7a1-ff0f01d013dc.jpeg	2025-11-27 02:20:55.353726+00	2025-11-27 10:18:10.026454+00	-6.14040260	106.88194120	Homefresh - Sunter Jaya, Jalan Danau Sunter Utara, Sunter Jaya, Tanjung Priok, Jakarta Utara, Daerah Khusus Ibukota Jakarta, Jawa, 14350, Indonesia	-6.20625920	106.80729600	Soto Sedaap Boyolali Hj. Widodo, 23, Jalan Pejompongan Baru, RW 05, Bendungan Hilir, Tanah Abang, Jakarta Pusat, Daerah Khusus Ibukota Jakarta, Jawa, 10210, Indonesia	\N
552	23	15	2025-11-27	present	2025-11-27 04:16:07.009201+00	2025-11-27 10:41:58.908653+00	6.43	23	2025-11-27 04:16:07.009201+00	112.78.141.78	\N	attendances/23/check_in/2025-11-27/859fc0a5-2b7c-4202-a4fc-dd5739666c9d.jpeg	2025-11-27 10:41:58.908653+00	112.78.141.78	\N	attendances/23/check_out/2025-11-27/e64657e4-ea16-4180-9a4c-abb30f93049a.jpeg	2025-11-27 04:16:08.087557+00	2025-11-27 10:41:59.832322+00	-6.14033386	106.88197957	Homefresh - Sunter Jaya, Jalan Danau Sunter Utara, Sunter Jaya, Tanjung Priok, Jakarta Utara, Daerah Khusus Ibukota Jakarta, Jawa, 14350, Indonesia	-6.14035850	106.88196681	Homefresh - Sunter Jaya, Jalan Danau Sunter Utara, Sunter Jaya, Tanjung Priok, Jakarta Utara, Daerah Khusus Ibukota Jakarta, Jawa, 14350, Indonesia	\N
1066	53	25	2025-12-15	present	2025-12-15 01:55:43.014214+00	2025-12-15 09:33:07.001968+00	7.62	53	2025-12-15 01:55:43.014214+00	114.10.102.194	\N	attendances/53/check_in/2025-12-15/a64ed4ad-eecc-42b7-b5fc-62bb48270c77.jpeg	2025-12-15 09:33:07.001968+00	103.87.231.107	\N	attendances/53/check_out/2025-12-15/9308e060-6414-42c8-bb5f-f192179c64b6.jpeg	2025-12-15 01:55:44.07104+00	2025-12-15 09:33:08.221985+00	-5.02821760	104.30416860	Jalan Raya Serengit, Mekar Sari, Lampung Barat, Lampung, Sumatra, Indonesia	-5.02820240	104.30405420	Jalan Raya Serengit, Mekar Sari, Lampung Barat, Lampung, Sumatra, Indonesia	0.00
566	13	10	2025-11-27	absent	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	2025-11-27 16:00:01.433008+00	2025-11-27 16:00:01.433013+00	\N	\N	\N	\N	\N	\N	\N
543	20	14	2025-11-27	invalid	2025-11-27 01:58:34.759286+00	\N	\N	20	2025-11-27 01:58:34.759286+00	114.10.101.186	\N	attendances/20/check_in/2025-11-27/58646902-c1c0-484f-8c30-f5192aba239b.jpeg	\N	\N	\N	\N	2025-11-27 01:58:35.277978+00	2025-11-27 16:59:00.143423+00	\N	\N	\N	\N	\N	\N	\N
595	13	10	2025-11-28	absent	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	2025-11-28 16:00:00.587268+00	2025-11-28 16:00:00.587272+00	\N	\N	\N	\N	\N	\N	\N
1061	58	27	2025-12-15	present	2025-12-15 01:25:16.429425+00	2025-12-15 09:41:55.224788+00	8.28	58	2025-12-15 01:25:16.429425+00	114.125.253.13	\N	attendances/58/check_in/2025-12-15/d6f3d2ff-47f6-4ab4-b3ee-27ac38376add.jpeg	2025-12-15 09:41:55.224788+00	180.242.4.50	\N	attendances/58/check_out/2025-12-15/06d35bfc-bdea-42fb-b5a7-3eb225333869.jpeg	2025-12-15 01:25:17.206234+00	2025-12-15 09:41:56.307719+00	-4.07509510	103.33491610	Dempo Selatan, Pagar Alam, Sumatera Selatan, Sumatra, Indonesia	-4.05605780	103.29806460	Rantau Unji, Dempo Tengah, Pagar Alam, Sumatera Selatan, Sumatra, Indonesia	0.00
1077	47	22	2025-12-15	present	2025-12-15 04:51:40.778854+00	2025-12-15 11:01:48.184472+00	6.17	47	2025-12-15 04:51:40.778854+00	182.3.105.26	\N	attendances/47/check_in/2025-12-15/bd496549-c33e-4965-b974-c1b81cc2fcb9.jpeg	2025-12-15 11:01:48.184472+00	182.3.105.26	\N	attendances/47/check_out/2025-12-15/1156f25c-c317-413e-ac40-76a393f3840f.jpeg	2025-12-15 04:51:42.338359+00	2025-12-15 11:01:58.087215+00	-5.38757860	105.28014340	Jalan Alam Kurnia, Kalibalau Kencana, Bandar Lampung, Lampung, Sumatra, 35133, Indonesia	-5.35864220	105.06165060	Tegalsari, Pringsewu, Lampung, Sumatra, 35367, Indonesia	0.00
573	23	15	2025-11-28	present	2025-11-28 01:02:04.89818+00	2025-11-28 16:35:12.546867+00	15.55	23	2025-11-28 01:02:04.89818+00	140.213.134.147	\N	attendances/23/check_in/2025-11-28/aa77d395-3535-4c89-8c73-d9cd955bcee2.jpeg	2025-11-28 16:35:12.546867+00	140.213.157.145	\N	attendances/23/check_out/2025-11-28/70c7b124-24e4-4537-8463-9055fb228720.jpeg	2025-11-28 01:02:06.512489+00	2025-11-28 16:35:13.738655+00	-5.92400308	105.99246750	Dermaga 7, Jalan Yos Sudarso, Kampungbaru Satu, Lebakgede, Cilegon, Banten, Jawa, 42438, Indonesia	-5.39623378	105.29563753	Sukarame, Bandar Lampung, Lampung, Sumatra, 35133, Indonesia	\N
1073	41	21	2025-12-15	present	2025-12-15 02:41:42.552372+00	2025-12-15 11:05:26.306576+00	8.40	41	2025-12-15 02:41:42.552372+00	103.105.82.243	\N	attendances/41/check_in/2025-12-15/8354fb09-84b5-4a70-be9b-f4fe3da49f35.jpeg	2025-12-15 11:05:26.306576+00	103.105.82.243	\N	attendances/41/check_out/2025-12-15/39dea03e-3246-4002-bc99-862608a91309.jpeg	2025-12-15 02:41:43.598902+00	2025-12-15 11:05:27.086071+00	-5.38757583	105.28018637	Jalan Alam Cantik, Kalibalau Kencana, Bandar Lampung, Lampung, Sumatra, 35133, Indonesia	-5.38759370	105.28023161	Jalan Alam Cantik, Kalibalau Kencana, Bandar Lampung, Lampung, Sumatra, 35133, Indonesia	0.00
1081	46	21	2025-12-15	absent	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	2025-12-15 16:00:01.01008+00	2025-12-15 16:00:01.01009+00	\N	\N	\N	\N	\N	\N	\N
1085	56	27	2025-12-15	absent	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	2025-12-15 16:00:01.298474+00	2025-12-15 16:00:01.298479+00	\N	\N	\N	\N	\N	\N	\N
1072	22	33	2025-12-15	invalid	2025-12-15 02:22:12.643052+00	\N	\N	22	2025-12-15 02:22:12.643052+00	103.105.82.243	\N	attendances/22/check_in/2025-12-15/4b0327ce-17ce-440d-a3e4-a49a039ee5e2.jpeg	\N	\N	\N	\N	2025-12-15 02:22:13.379778+00	2025-12-15 16:30:00.069239+00	-5.39387250	105.27800970	Kalibalau Kencana, Bandar Lampung, Lampung, Sumatra, 35136, Indonesia	\N	\N	\N	\N
1091	60	29	2025-12-16	present	2025-12-16 00:10:00.779523+00	2025-12-16 08:13:08.067817+00	8.05	60	2025-12-16 00:10:00.779523+00	103.145.34.18	\N	attendances/60/check_in/2025-12-16/b9afb7d9-9089-48b0-b11f-e469e6b6926b.jpeg	2025-12-16 08:13:08.067817+00	114.10.100.207	\N	attendances/60/check_out/2025-12-16/7d22e0b7-3989-4c20-8a3b-97ed385f7f7c.jpeg	2025-12-16 00:10:01.850776+00	2025-12-16 08:13:09.854094+00	-5.42568770	104.73793860	Kota Dalam, Tanggamus, Lampung, Sumatra, Indonesia	-5.47747500	104.75468170	Menggala, Tanggamus, Lampung, Sumatra, Indonesia	0.00
1108	55	27	2025-12-16	present	2025-12-16 02:47:42.987129+00	2025-12-16 10:11:12.250371+00	7.39	55	2025-12-16 02:47:42.987129+00	114.10.98.233	Pagaralam	attendances/55/check_in/2025-12-16/6cb4de00-8afc-488b-883f-11c52e2df891.jpeg	2025-12-16 10:11:12.250371+00	114.10.98.136	\N	attendances/55/check_out/2025-12-16/50b44716-3052-4213-b25b-b9722a857d16.jpeg	2025-12-16 02:47:43.945586+00	2025-12-16 10:11:13.431795+00	-4.05607140	103.29806280	Rantau Unji, Dempo Tengah, Pagar Alam, Sumatera Selatan, Sumatra, Indonesia	-4.05607400	103.29807100	Rantau Unji, Dempo Tengah, Pagar Alam, Sumatera Selatan, Sumatra, Indonesia	0.00
1104	41	21	2025-12-16	present	2025-12-16 02:22:06.126676+00	2025-12-16 10:28:04.406192+00	8.10	41	2025-12-16 02:22:06.126676+00	114.10.100.152	\N	attendances/41/check_in/2025-12-16/a1f710d3-9145-4519-9bfe-1632738aa30b.jpeg	2025-12-16 10:28:04.406192+00	103.105.82.243	\N	attendances/41/check_out/2025-12-16/e11758fe-7f0c-4186-b15b-0f9b7bcdaabf.jpeg	2025-12-16 02:22:07.197556+00	2025-12-16 10:28:05.167965+00	-5.38757346	105.28018675	Jalan Alam Cantik, Kalibalau Kencana, Bandar Lampung, Lampung, Sumatra, 35133, Indonesia	-5.38757342	105.28018954	Jalan Alam Cantik, Kalibalau Kencana, Bandar Lampung, Lampung, Sumatra, 35133, Indonesia	0.00
1105	22	33	2025-12-16	present	2025-12-16 02:32:42.205277+00	2025-12-16 10:29:33.218822+00	7.95	22	2025-12-16 02:32:42.205277+00	114.10.103.203	\N	attendances/22/check_in/2025-12-16/dd1f4b3c-4c81-4d45-ac85-69b70e2b83a3.jpeg	2025-12-16 10:29:33.218822+00	103.105.82.243	\N	attendances/22/check_out/2025-12-16/ab996177-f3eb-4914-b3b5-48175b39101e.jpeg	2025-12-16 02:32:43.166535+00	2025-12-16 10:29:33.923318+00	-5.38705920	105.25736960	Gang Manggis, Sidodadi, Bandar Lampung, Lampung, Sumatra, 35123, Indonesia	-5.38705920	105.25736960	Gang Manggis, Sidodadi, Bandar Lampung, Lampung, Sumatra, 35123, Indonesia	0.00
1100	52	24	2025-12-16	present	2025-12-16 01:32:26.071029+00	2025-12-16 10:39:56.339152+00	9.13	52	2025-12-16 01:32:26.071029+00	114.10.102.155	\N	attendances/52/check_in/2025-12-16/2dadf2da-369f-4ff4-8a5d-0bb639d857dd.jpeg	2025-12-16 10:39:56.339152+00	114.10.100.111	\N	attendances/52/check_out/2025-12-16/70047f5d-6c95-4b00-a5d5-c862038926bb.jpeg	2025-12-16 01:32:26.830984+00	2025-12-16 10:40:03.577802+00	-5.02816140	104.30413330	Jalan Raya Serengit, Mekar Sari, Lampung Barat, Lampung, Sumatra, Indonesia	-5.02823340	104.30404670	Jalan Raya Serengit, Mekar Sari, Lampung Barat, Lampung, Sumatra, Indonesia	0.00
1099	54	25	2025-12-16	present	2025-12-16 01:29:50.730298+00	2025-12-16 10:40:36.900702+00	9.18	54	2025-12-16 01:29:50.730298+00	103.87.231.107	\N	attendances/54/check_in/2025-12-16/eccf5cea-fb13-4039-8240-8fe9b034efe6.jpeg	2025-12-16 10:40:36.900702+00	114.10.102.226	\N	attendances/54/check_out/2025-12-16/a95fc798-6d35-4aa9-b120-a69e4e278b06.jpeg	2025-12-16 01:29:51.444061+00	2025-12-16 10:40:38.936464+00	-5.02823860	104.30404000	Jalan Raya Serengit, Mekar Sari, Lampung Barat, Lampung, Sumatra, Indonesia	-5.02822890	104.30404210	Jalan Raya Serengit, Mekar Sari, Lampung Barat, Lampung, Sumatra, Indonesia	0.00
1102	53	25	2025-12-16	present	2025-12-16 02:01:52.370555+00	2025-12-16 10:48:19.097537+00	8.77	53	2025-12-16 02:01:52.370555+00	114.10.102.221	\N	attendances/53/check_in/2025-12-16/384b8e28-745d-464f-9433-5461ac61bf0c.jpeg	2025-12-16 10:48:19.097537+00	103.87.231.107	\N	attendances/53/check_out/2025-12-16/27e178da-1613-4e70-b280-87fd15c25308.jpeg	2025-12-16 02:01:53.073349+00	2025-12-16 10:48:22.841688+00	-5.02823130	104.30404700	Jalan Raya Serengit, Mekar Sari, Lampung Barat, Lampung, Sumatra, Indonesia	-5.02822890	104.30404860	Jalan Raya Serengit, Mekar Sari, Lampung Barat, Lampung, Sumatra, Indonesia	0.00
1103	24	31	2025-12-16	present	2025-12-16 02:03:14.81549+00	2025-12-16 10:55:57.758458+00	8.88	24	2025-12-16 02:03:14.81549+00	103.105.82.243	\N	attendances/24/check_in/2025-12-16/b7cb2c56-5518-4937-80bc-43eb932d190e.jpeg	2025-12-16 10:55:57.758458+00	103.105.82.243	\N	attendances/24/check_out/2025-12-16/25e7e4af-e100-4f47-9849-df20ca06fe33.jpeg	2025-12-16 02:03:15.571759+00	2025-12-16 10:55:58.751709+00	-5.38758470	105.28015700	Jalan Alam Kurnia, Kalibalau Kencana, Bandar Lampung, Lampung, Sumatra, 35133, Indonesia	-5.38757340	105.28013000	Jalan Alam Kurnia, Kalibalau Kencana, Bandar Lampung, Lampung, Sumatra, 35133, Indonesia	0.00
1090	61	29	2025-12-16	present	2025-12-16 00:03:51.214283+00	2025-12-16 13:41:40.578275+00	13.63	61	2025-12-16 00:03:51.214283+00	114.10.102.211	\N	attendances/61/check_in/2025-12-16/7f501f94-a6d3-4a91-b837-e777844d5c1b.jpeg	2025-12-16 13:41:40.578275+00	114.10.102.101	Update data pembibitan	attendances/61/check_out/2025-12-16/7b0244d0-6aea-477c-aa04-6a7ffc14361c.jpeg	2025-12-16 00:03:52.242799+00	2025-12-16 13:41:41.691917+00	-5.05141210	104.10741350	Gang Buntu, Liwa, Lampung Barat, Lampung, Sumatra, 34812, Indonesia	-5.05158500	104.10735500	Gang Buntu, Liwa, Lampung Barat, Lampung, Sumatra, 34812, Indonesia	0.00
1116	56	27	2025-12-16	absent	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	2025-12-16 16:00:00.298205+00	2025-12-16 16:00:00.298209+00	\N	\N	\N	\N	\N	\N	\N
1120	43	32	2025-12-16	hybrid	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	2025-12-16 16:00:00.338705+00	2025-12-16 16:00:00.338709+00	\N	\N	\N	\N	\N	\N	\N
1101	64	24	2025-12-16	invalid	2025-12-16 02:00:17.194844+00	\N	\N	64	2025-12-16 02:00:17.194844+00	110.137.39.211	\N	attendances/64/check_in/2025-12-16/a1f490b0-563f-467f-9e20-6a9a710e1759.jpeg	\N	\N	\N	\N	2025-12-16 02:00:18.296813+00	2025-12-16 16:30:00.056822+00	-4.85927062	104.93110968	Tanjung Harapan, Lampung Utara, Lampung, Sumatra, 34511, Indonesia	\N	\N	\N	\N
579	39	17	2025-11-28	present	2025-11-28 04:27:10.199565+00	2025-11-28 15:19:39.009988+00	10.87	39	2025-11-28 04:27:10.199565+00	182.3.105.114	\N	attendances/39/check_in/2025-11-28/cfae9a97-75f5-4b73-9b8c-4e99386869bf.jpeg	2025-11-28 15:19:39.009988+00	114.10.102.15	\N	attendances/39/check_out/2025-11-28/47fd2182-d610-45d7-84c3-fbaa85ae76a9.jpeg	2025-11-28 04:27:11.280692+00	2025-11-28 15:19:40.669822+00	-5.36384500	105.30365170	Bandar Lampung, Lampung, Sumatra, 35131, Indonesia	-5.44118360	105.29601500	Jalan Perumahan Garuntang Lestari, Way Lunik, Bandar Lampung, Lampung, Sumatra, 35245, Indonesia	\N
583	22	15	2025-11-28	absent	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	2025-11-28 16:00:00.503494+00	2025-11-28 16:00:00.503499+00	\N	\N	\N	\N	\N	\N	\N
727	24	15	2025-12-04	present	2025-12-04 01:58:56.809813+00	2025-12-04 14:13:51.042875+00	12.25	24	2025-12-04 01:58:56.809813+00	103.105.82.245	\N	attendances/24/check_in/2025-12-04/ba51633f-d137-4881-a0f9-97de6fba4370.jpeg	2025-12-04 14:13:51.042875+00	114.10.102.67	\N	attendances/24/check_out/2025-12-04/99582e95-6bcd-45b0-89c8-aae0e143c9bc.jpeg	2025-12-04 01:58:58.108597+00	2025-12-04 15:03:57.967025+00	-5.38757690	105.28013800	Jalan Alam Kurnia, Kalibalau Kencana, Bandar Lampung, Lampung, Sumatra, 35133, Indonesia	-5.38758590	105.28015770	Jalan Alam Kurnia, Kalibalau Kencana, Bandar Lampung, Lampung, Sumatra, 35133, Indonesia	0.00
605	23	15	2025-11-29	present	2025-11-29 02:06:27.121856+00	2025-11-29 08:31:27.477986+00	6.42	23	2025-11-29 02:06:27.121856+00	182.3.101.125	\N	attendances/23/check_in/2025-11-29/8cc79ee1-6d01-4c79-a835-749c65ec5f9b.jpeg	2025-11-29 08:31:27.477986+00	140.213.116.30	\N	attendances/23/check_out/2025-11-29/11d95df4-8ac0-469a-b4a0-08baa4a4d434.jpeg	2025-11-29 02:06:27.96643+00	2025-11-29 08:31:28.760158+00	-5.43050929	104.73906198	Gisting Bawah, Tanggamus, Lampung, Sumatra, Indonesia	-5.43050542	104.73904248	Gisting Bawah, Tanggamus, Lampung, Sumatra, Indonesia	\N
607	41	12	2025-11-29	present	2025-11-29 02:12:47.984855+00	2025-11-29 08:57:02.808283+00	6.74	41	2025-11-29 02:12:47.984855+00	103.59.44.25	\N	attendances/41/check_in/2025-11-29/8e3852f0-c68d-4ead-a769-d534df801f47.jpeg	2025-11-29 08:57:02.808283+00	114.10.102.134	\N	attendances/41/check_out/2025-11-29/9b22255c-3460-47f1-808b-d79cb961f35b.jpeg	2025-11-29 02:12:48.991998+00	2025-11-29 08:57:03.844237+00	-5.43058190	104.73916070	Gisting Bawah, Tanggamus, Lampung, Sumatra, Indonesia	-5.43042844	104.73911656	Gisting Bawah, Tanggamus, Lampung, Sumatra, Indonesia	\N
606	40	11	2025-11-29	present	2025-11-29 02:06:32.7458+00	2025-11-29 08:59:43.171557+00	6.89	40	2025-11-29 02:06:32.7458+00	103.59.44.25	Dinas tanggamus	attendances/40/check_in/2025-11-29/c621ebab-764d-4215-aa38-b3eb400234f0.jpeg	2025-11-29 08:59:43.171557+00	103.59.44.25	\N	attendances/40/check_out/2025-11-29/8d1c661c-df46-48de-a051-f399c076d9cd.jpeg	2025-11-29 02:06:33.510042+00	2025-11-29 08:59:43.978464+00	-5.43048838	104.73909693	Gisting Bawah, Tanggamus, Lampung, Sumatra, Indonesia	-5.43293440	104.73635840	Gisting Bawah, Tanggamus, Lampung, Sumatra, Indonesia	\N
603	15	12	2025-11-29	present	2025-11-29 01:38:50.66358+00	2025-11-29 09:12:41.60685+00	7.56	15	2025-11-29 01:38:50.66358+00	182.3.100.143	\N	attendances/15/check_in/2025-11-29/08654293-a08c-44de-9927-01df55877ed2.jpeg	2025-11-29 09:12:41.60685+00	182.3.105.84	\N	attendances/15/check_out/2025-11-29/b0fa3a5f-56ab-49f3-a10a-8d571eec525b.jpeg	2025-11-29 01:38:52.3008+00	2025-11-29 09:12:42.629489+00	-5.43053770	104.73912150	Gisting Bawah, Tanggamus, Lampung, Sumatra, Indonesia	-5.43019050	104.73558290	Gisting Bawah, Tanggamus, Lampung, Sumatra, Indonesia	\N
604	42	11	2025-11-29	present	2025-11-29 02:03:41.190824+00	2025-11-29 09:41:50.955009+00	7.64	42	2025-11-29 02:03:41.190824+00	103.59.44.25	\N	attendances/42/check_in/2025-11-29/26dc8e9f-f3e6-467d-854a-88f5f5778dfd.jpeg	2025-11-29 09:41:50.955009+00	182.3.100.199	\N	attendances/42/check_out/2025-11-29/63d7db84-fb26-464b-ac00-f7a5814b7267.jpeg	2025-11-29 02:03:42.191542+00	2025-11-29 09:41:52.16285+00	-5.43056740	104.73915630	Gisting Bawah, Tanggamus, Lampung, Sumatra, Indonesia	-5.36334120	104.78463250	Jalan Raya Kota Agung - Pring Sewu, Banding Agung, Tanggamus, Lampung, Sumatra, Indonesia	\N
609	24	15	2025-11-29	present	2025-11-29 07:16:56.842484+00	2025-11-29 10:04:10.525086+00	2.79	24	2025-11-29 07:16:56.842484+00	114.10.102.174	\N	attendances/24/check_in/2025-11-29/8c271b63-4695-4549-b8be-e0ee9d672618.jpeg	2025-11-29 10:04:10.525086+00	114.10.102.174	\N	attendances/24/check_out/2025-11-29/b00732d8-a732-4474-97c8-d5815ecddd2c.jpeg	2025-11-29 07:16:58.255565+00	2025-11-29 10:04:11.423361+00	-5.35798320	104.98075970	Jalan Melati 2, Pringsewu, Lampung, Sumatra, 35373, Indonesia	-5.31273560	104.95969150	Sukoharjo I, Pringsewu, Lampung, Sumatra, 35373, Indonesia	\N
1074	15	21	2025-12-15	present	2025-12-15 03:01:17.935887+00	2025-12-15 09:04:31.407887+00	6.05	15	2025-12-15 03:01:17.935887+00	182.3.102.172	\N	attendances/15/check_in/2025-12-15/c7fafbb6-7f58-4ef1-b0d7-cb4663e25e77.jpeg	2025-12-15 09:04:31.407887+00	103.105.82.243	\N	attendances/15/check_out/2025-12-15/e3f964b0-f34d-47eb-afff-0771586ea33e.jpeg	2025-12-15 03:01:19.498188+00	2025-12-15 09:04:32.831392+00	-5.38630130	105.27962460	Way Halim Permai, Bandar Lampung, Lampung, Sumatra, 35133, Indonesia	-5.38758520	105.28015610	Jalan Alam Kurnia, Kalibalau Kencana, Bandar Lampung, Lampung, Sumatra, 35133, Indonesia	0.00
1079	55	27	2025-12-15	present	2025-12-15 07:05:54.659378+00	2025-12-15 12:05:47.768004+00	5.00	55	2025-12-15 07:05:54.659378+00	114.10.98.201	Pagaralam	attendances/55/check_in/2025-12-15/93e24c8e-fe93-4bdb-8200-c1ca88da1508.jpeg	2025-12-15 12:05:47.768004+00	114.10.98.233	Pagaralam	attendances/55/check_out/2025-12-15/92cac91a-a417-4636-88f8-66613e0e8137.jpeg	2025-12-15 07:05:55.912084+00	2025-12-15 12:05:48.877792+00	-4.02402830	103.25514360	Pagar Alam Selatan, Pagar Alam, Sumatera Selatan, Sumatra, Indonesia	-4.05607260	103.29806960	Rantau Unji, Dempo Tengah, Pagar Alam, Sumatera Selatan, Sumatra, Indonesia	0.00
623	13	10	2025-11-29	absent	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	2025-11-29 16:00:00.157373+00	2025-11-29 16:00:00.157378+00	\N	\N	\N	\N	\N	\N	\N
624	14	11	2025-11-29	absent	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	2025-11-29 16:00:00.161583+00	2025-11-29 16:00:00.161587+00	\N	\N	\N	\N	\N	\N	\N
630	39	17	2025-11-29	hybrid	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	2025-11-29 16:00:00.200643+00	2025-11-29 16:00:00.200648+00	\N	\N	\N	\N	\N	\N	\N
631	43	17	2025-11-29	hybrid	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	2025-11-29 16:00:00.213642+00	2025-11-29 16:00:00.213647+00	\N	\N	\N	\N	\N	\N	\N
632	44	17	2025-11-29	absent	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	2025-11-29 16:00:00.222287+00	2025-11-29 16:00:00.222293+00	\N	\N	\N	\N	\N	\N	\N
608	22	15	2025-11-29	invalid	2025-11-29 04:19:23.353671+00	\N	\N	22	2025-11-29 04:19:23.353671+00	103.130.18.0	\N	attendances/22/check_in/2025-11-29/c3bdde10-08d8-465e-b946-7872da6df72d.jpeg	\N	\N	\N	\N	2025-11-29 04:19:24.52877+00	2025-11-29 16:30:00.011029+00	-5.36016420	105.24744050	Sepang Jaya, Bandar Lampung, Lampung, Sumatra, 35141, Indonesia	\N	\N	\N	\N
610	20	14	2025-11-29	invalid	2025-11-29 10:03:35.563309+00	\N	\N	20	2025-11-29 10:03:35.563309+00	114.10.101.79	\N	attendances/20/check_in/2025-11-29/86dc3a5e-c8d6-4415-a393-f0be26f99c49.jpeg	\N	\N	\N	\N	2025-11-29 10:03:35.808925+00	2025-11-29 16:30:00.013921+00	\N	\N	\N	\N	\N	\N	\N
633	40	11	2025-11-30	absent	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	2025-11-30 16:00:00.153492+00	2025-11-30 16:00:00.153498+00	\N	\N	\N	\N	\N	\N	\N
634	41	12	2025-11-30	absent	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	2025-11-30 16:00:00.205376+00	2025-11-30 16:00:00.20538+00	\N	\N	\N	\N	\N	\N	\N
635	42	11	2025-11-30	absent	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	2025-11-30 16:00:00.219301+00	2025-11-30 16:00:00.219306+00	\N	\N	\N	\N	\N	\N	\N
636	44	17	2025-11-30	absent	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	2025-11-30 16:00:00.232566+00	2025-11-30 16:00:00.232571+00	\N	\N	\N	\N	\N	\N	\N
639	40	11	2025-12-01	present	2025-12-01 02:21:26.643539+00	2025-12-01 10:07:32.445294+00	7.77	40	2025-12-01 02:21:26.643539+00	103.105.82.245	\N	attendances/40/check_in/2025-12-01/7611dc3b-d21e-49b7-91a5-41321ed05606.jpeg	2025-12-01 10:07:32.445294+00	103.105.82.245	\N	attendances/40/check_out/2025-12-01/7bf5fcc8-02b9-40bc-ab39-8634fa77cbd3.jpeg	2025-12-01 02:21:27.945673+00	2025-12-01 10:07:33.185674+00	-0.78927500	113.92132700	Kapuas, Kalimantan Tengah, Kalimantan, Indonesia	-5.37694320	105.26776770	Perumnas Way Halim, Bandar Lampung, Lampung, Sumatra, 35132, Indonesia	0.00
638	24	15	2025-12-01	present	2025-12-01 02:00:39.253189+00	2025-12-01 11:06:26.395466+00	9.10	24	2025-12-01 02:00:39.253189+00	103.105.82.245	\N	attendances/24/check_in/2025-12-01/9ce50c93-6310-45e9-973d-e95350cb849d.jpeg	2025-12-01 11:06:26.395466+00	114.10.100.71	\N	attendances/24/check_out/2025-12-01/96b25e17-44b4-47b2-a2e8-f55132f5661b.jpeg	2025-12-01 02:00:40.505732+00	2025-12-01 11:06:27.174362+00	-5.38758050	105.28016200	Jalan Alam Cantik, Kalibalau Kencana, Bandar Lampung, Lampung, Sumatra, 35133, Indonesia	-5.38757970	105.28016030	Jalan Alam Cantik, Kalibalau Kencana, Bandar Lampung, Lampung, Sumatra, 35133, Indonesia	0.00
641	20	14	2025-12-01	invalid	2025-12-01 02:36:20.13357+00	\N	\N	20	2025-12-01 02:36:20.13357+00	103.105.82.245	\N	attendances/20/check_in/2025-12-01/8b55285e-e301-400a-93ea-326c2722f21a.jpeg	\N	\N	\N	\N	2025-12-01 02:36:21.122287+00	2025-12-01 16:30:00.105305+00	-0.78927500	113.92132700	Kapuas, Kalimantan Tengah, Kalimantan, Indonesia	\N	\N	\N	\N
643	15	12	2025-12-01	present	2025-12-01 02:50:43.511833+00	2025-12-01 09:48:15.645942+00	6.96	15	2025-12-01 02:50:43.511833+00	103.105.82.245	\N	attendances/15/check_in/2025-12-01/76a50759-7b68-49d4-b36b-d88067fed8bb.jpeg	2025-12-01 09:48:15.645942+00	103.105.82.245	\N	attendances/15/check_out/2025-12-01/0cbe6879-521b-48ae-b63d-59ce5808d527.jpeg	2025-12-01 02:50:44.538939+00	2025-12-01 09:48:16.714218+00	-5.38757870	105.28015620	Jalan Alam Cantik, Kalibalau Kencana, Bandar Lampung, Lampung, Sumatra, 35133, Indonesia	-5.38757870	105.28015620	Jalan Alam Cantik, Kalibalau Kencana, Bandar Lampung, Lampung, Sumatra, 35133, Indonesia	0.00
645	14	11	2025-12-01	present	2025-12-01 09:42:38.46515+00	2025-12-01 10:47:48.226365+00	1.09	14	2025-12-01 09:42:38.46515+00	103.105.82.245	\N	attendances/14/check_in/2025-12-01/e08a22c5-7c8b-4fc5-9d01-8cb7cde3e5f3.jpeg	2025-12-01 10:47:48.226365+00	103.105.82.245	\N	attendances/14/check_out/2025-12-01/4924cff8-0843-4027-9b99-357e0d626907.jpeg	2025-12-01 09:42:40.129015+00	2025-12-01 10:47:49.254631+00	-5.37694320	105.26776770	Perumnas Way Halim, Bandar Lampung, Lampung, Sumatra, 35132, Indonesia	-5.37694320	105.26776770	Perumnas Way Halim, Bandar Lampung, Lampung, Sumatra, 35132, Indonesia	0.00
644	44	17	2025-12-01	present	2025-12-01 03:08:19.795637+00	2025-12-01 11:05:44.9605+00	7.96	44	2025-12-01 03:08:19.795637+00	114.10.102.251	\N	attendances/44/check_in/2025-12-01/ffe2ecfe-db4c-4a13-a4d6-519866437474.jpeg	2025-12-01 11:05:44.9605+00	103.105.82.245	\N	attendances/44/check_out/2025-12-01/a1e0a545-953f-4a1d-8737-02cd61be2a73.jpeg	2025-12-01 03:08:20.695658+00	2025-12-01 11:05:46.944147+00	-5.38758020	105.28016000	Jalan Alam Cantik, Kalibalau Kencana, Bandar Lampung, Lampung, Sumatra, 35133, Indonesia	-5.38757900	105.28015940	Jalan Alam Cantik, Kalibalau Kencana, Bandar Lampung, Lampung, Sumatra, 35133, Indonesia	0.00
647	23	15	2025-12-01	absent	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	2025-12-01 16:00:00.684366+00	2025-12-01 16:00:00.684371+00	\N	\N	\N	\N	\N	\N	\N
1070	42	28	2025-12-15	present	2025-12-15 02:20:13.376615+00	2025-12-15 10:02:24.903991+00	7.70	42	2025-12-15 02:20:13.376615+00	103.105.82.243	\N	attendances/42/check_in/2025-12-15/75a6788b-1d1a-4cdb-9063-f407c4e52d44.jpeg	2025-12-15 10:02:24.903991+00	103.105.82.243	\N	attendances/42/check_out/2025-12-15/f6a0ea1c-0da7-490f-9d46-4fd0f8b364e3.jpeg	2025-12-15 02:20:14.12684+00	2025-12-15 10:02:28.766279+00	-5.38758490	105.28015890	Jalan Alam Kurnia, Kalibalau Kencana, Bandar Lampung, Lampung, Sumatra, 35133, Indonesia	-5.38758500	105.28015840	Jalan Alam Kurnia, Kalibalau Kencana, Bandar Lampung, Lampung, Sumatra, 35133, Indonesia	0.00
659	13	10	2025-12-01	absent	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	2025-12-01 16:00:00.848294+00	2025-12-01 16:00:00.848298+00	\N	\N	\N	\N	\N	\N	\N
1076	44	34	2025-12-15	present	2025-12-15 03:30:03.012115+00	2025-12-15 10:36:53.059618+00	7.11	44	2025-12-15 03:30:03.012115+00	114.10.102.244	\N	attendances/44/check_in/2025-12-15/30ace2fe-6498-4b4f-8ffb-7f57e3bb1dd2.jpeg	2025-12-15 10:36:53.059618+00	114.10.102.244	\N	attendances/44/check_out/2025-12-15/2173a12e-be0c-4031-8e7b-a8445450dae9.jpeg	2025-12-15 03:30:04.492673+00	2025-12-15 10:36:53.861672+00	-5.38758590	105.28015930	Jalan Alam Kurnia, Kalibalau Kencana, Bandar Lampung, Lampung, Sumatra, 35133, Indonesia	-5.38368120	105.27551370	Jalan Griya Taman I, Way Halim Permai, Bandar Lampung, Lampung, Sumatra, 35136, Indonesia	0.00
667	24	15	2025-12-02	present	2025-12-02 01:55:55.461927+00	2025-12-02 10:11:46.641346+00	8.26	24	2025-12-02 01:55:55.461927+00	103.105.82.245	\N	attendances/24/check_in/2025-12-02/324fe5b1-e1cd-46a8-ba3d-6662d4e4c853.jpeg	2025-12-02 10:11:46.641346+00	103.105.82.245	\N	attendances/24/check_out/2025-12-02/224c2b7a-527f-4b50-a554-8567ab64d9e1.jpeg	2025-12-02 01:55:56.829631+00	2025-12-02 10:11:47.431724+00	-5.37694320	105.26776770	Perumnas Way Halim, Bandar Lampung, Lampung, Sumatra, 35132, Indonesia	-5.37694320	105.26776770	Perumnas Way Halim, Bandar Lampung, Lampung, Sumatra, 35132, Indonesia	0.00
669	23	15	2025-12-02	present	2025-12-02 02:00:57.878125+00	2025-12-02 10:17:31.605007+00	8.28	23	2025-12-02 02:00:57.878125+00	103.105.82.245	\N	attendances/23/check_in/2025-12-02/96d4b4ab-83b9-4919-8c80-746e83b9a3cd.jpeg	2025-12-02 10:17:31.605007+00	140.213.116.228	\N	attendances/23/check_out/2025-12-02/c501de90-8294-423e-8af8-9e6cd47e24ec.jpeg	2025-12-02 02:00:58.782889+00	2025-12-02 10:17:32.407312+00	-5.38756836	105.28013876	Jalan Alam Kurnia, Kalibalau Kencana, Bandar Lampung, Lampung, Sumatra, 35133, Indonesia	-5.38751758	105.28013356	Jalan Alam Cantik, Kalibalau Kencana, Bandar Lampung, Lampung, Sumatra, 35133, Indonesia	0.00
675	14	11	2025-12-02	present	2025-12-02 03:58:12.759782+00	2025-12-02 10:34:58.116553+00	6.61	14	2025-12-02 03:58:12.759782+00	103.105.82.245	\N	attendances/14/check_in/2025-12-02/a1f290e4-a450-48ff-b25d-0e852d7a979a.jpeg	2025-12-02 10:34:58.116553+00	103.105.82.245	\N	attendances/14/check_out/2025-12-02/edb38736-b54b-46ea-8b7b-e85018602e74.jpeg	2025-12-02 03:58:13.687288+00	2025-12-02 10:34:59.11975+00	-5.37694320	105.26776770	Perumnas Way Halim, Bandar Lampung, Lampung, Sumatra, 35132, Indonesia	-5.39243230	105.25606330	Sukamenanti, Bandar Lampung, Lampung, Sumatra, 35123, Indonesia	0.00
1084	48	23	2025-12-15	absent	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	2025-12-15 16:00:01.272092+00	2025-12-15 16:00:01.272096+00	\N	\N	\N	\N	\N	\N	\N
1088	43	32	2025-12-15	hybrid	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	2025-12-15 16:00:01.431967+00	2025-12-15 16:00:01.431972+00	\N	\N	\N	\N	\N	\N	\N
1110	15	21	2025-12-16	present	2025-12-16 03:08:01.236773+00	2025-12-16 09:44:26.770581+00	6.61	15	2025-12-16 03:08:01.236773+00	182.3.104.118	\N	attendances/15/check_in/2025-12-16/b45ea75d-8cef-4676-8405-18d765d674da.jpeg	2025-12-16 09:44:26.770581+00	103.105.82.243	\N	attendances/15/check_out/2025-12-16/e8d2cb44-3f48-40b1-9254-8537353cdf29.jpeg	2025-12-16 03:08:02.297492+00	2025-12-16 09:44:27.835538+00	-5.38627030	105.27961430	Way Halim Permai, Bandar Lampung, Lampung, Sumatra, 35133, Indonesia	-5.38758470	105.28015730	Jalan Alam Kurnia, Kalibalau Kencana, Bandar Lampung, Lampung, Sumatra, 35133, Indonesia	0.00
1112	47	22	2025-12-16	present	2025-12-16 03:21:46.219845+00	2025-12-16 10:04:43.40011+00	6.72	47	2025-12-16 03:21:46.219845+00	182.3.68.164	\N	attendances/47/check_in/2025-12-16/82fc336b-1b01-4a24-b3da-4f842ac89a50.jpeg	2025-12-16 10:04:43.40011+00	182.3.68.164	\N	attendances/47/check_out/2025-12-16/76570ad8-83fa-4a91-acb2-21ac41675078.jpeg	2025-12-16 03:21:47.247022+00	2025-12-16 10:04:44.440436+00	-5.43056890	104.73916010	Gisting Bawah, Tanggamus, Lampung, Sumatra, Indonesia	-5.35856650	105.06165780	Tegalsari, Pringsewu, Lampung, Sumatra, 35367, Indonesia	0.00
1109	42	28	2025-12-16	present	2025-12-16 02:57:34.837952+00	2025-12-16 10:05:52.483096+00	7.14	42	2025-12-16 02:57:34.837952+00	103.105.82.243	\N	attendances/42/check_in/2025-12-16/c45e8e4e-fe0b-477d-91aa-c0080c897694.jpeg	2025-12-16 10:05:52.483096+00	103.105.82.243	\N	attendances/42/check_out/2025-12-16/89ec0497-b455-4297-b758-1e446348eb5e.jpeg	2025-12-16 02:57:35.858274+00	2025-12-16 10:05:53.295062+00	-5.38758220	105.28015970	Jalan Alam Cantik, Kalibalau Kencana, Bandar Lampung, Lampung, Sumatra, 35133, Indonesia	-5.38758390	105.28015810	Jalan Alam Kurnia, Kalibalau Kencana, Bandar Lampung, Lampung, Sumatra, 35133, Indonesia	0.00
1095	51	23	2025-12-16	present	2025-12-16 01:12:09.916123+00	2025-12-16 10:11:34.289062+00	8.99	51	2025-12-16 01:12:09.916123+00	103.59.44.25	\N	attendances/51/check_in/2025-12-16/8fbe2bef-adbe-4f0b-807e-17be9f4a1b97.jpeg	2025-12-16 10:11:34.289062+00	182.3.104.43	\N	attendances/51/check_out/2025-12-16/4393214d-76f1-4bca-bd46-badcf524c6a0.jpeg	2025-12-16 01:12:10.711884+00	2025-12-16 10:11:36.593869+00	-5.43050790	104.73907060	Gisting Bawah, Tanggamus, Lampung, Sumatra, Indonesia	-5.43059330	104.73905670	Gisting Bawah, Tanggamus, Lampung, Sumatra, Indonesia	0.00
1106	57	27	2025-12-16	present	2025-12-16 02:35:11.586607+00	2025-12-16 10:26:54.258549+00	7.86	57	2025-12-16 02:35:11.586607+00	180.242.4.50	pagar alam	attendances/57/check_in/2025-12-16/4fd758ff-d1ad-446c-9645-d9e6e57bf76f.jpeg	2025-12-16 10:26:54.258549+00	140.213.65.21	\N	attendances/57/check_out/2025-12-16/06498da1-a45f-4c53-9a65-fd28716f6f57.jpeg	2025-12-16 02:35:12.401858+00	2025-12-16 10:26:56.250564+00	-4.05599171	103.29804450	Rantau Unji, Dempo Tengah, Pagar Alam, Sumatera Selatan, Sumatra, Indonesia	-4.05617416	103.29808595	Rantau Unji, Dempo Tengah, Pagar Alam, Sumatera Selatan, Sumatra, Indonesia	0.00
1089	14	28	2025-12-16	invalid	2025-12-15 22:44:28.207472+00	2025-12-16 16:44:38.037186+00	18.00	14	2025-12-15 22:44:28.207472+00	182.2.164.23	\N	attendances/14/check_in/2025-12-16/1199368f-41ff-4977-a72b-0fc75811297a.jpeg	2025-12-16 16:44:38.037186+00	182.3.37.183	\N	attendances/14/check_out/2025-12-16/b3aecb96-911c-49ce-a85f-df6db86c57ba.jpeg	2025-12-15 22:44:29.813908+00	2025-12-16 16:44:39.991928+00	-6.18517420	106.82030060	Jalan Kampung Bali X, RW 09, Kampung Bali, Tanah Abang, Jakarta Pusat, Daerah Khusus Ibukota Jakarta, Jawa, 10250, Indonesia	-7.01111790	107.52911460	Parungserab, Kabupaten Bandung, Jawa, 40319, Indonesia	0.00
640	42	11	2025-12-01	present	2025-12-01 02:30:21.489088+00	2025-12-01 10:03:29.064207+00	7.55	42	2025-12-01 02:30:21.489088+00	103.105.82.245	\N	attendances/42/check_in/2025-12-01/3321cc7e-32aa-4ea0-8d4b-b91f4623eb52.jpeg	2025-12-01 10:03:29.064207+00	103.105.82.245	\N	attendances/42/check_out/2025-12-01/a367a233-5924-46fe-b214-6a55335a910a.jpeg	2025-12-01 02:30:23.149167+00	2025-12-01 10:03:30.388772+00	-5.38758110	105.28016070	Jalan Alam Cantik, Kalibalau Kencana, Bandar Lampung, Lampung, Sumatra, 35133, Indonesia	-5.38763640	105.28013860	Jalan Alam Kurnia, Kalibalau Kencana, Bandar Lampung, Lampung, Sumatra, 35133, Indonesia	0.00
1078	39	32	2025-12-15	present	2025-12-15 04:53:18.221119+00	2025-12-15 09:46:35.304887+00	4.89	39	2025-12-15 04:53:18.221119+00	114.10.100.149	\N	attendances/39/check_in/2025-12-15/21c4e996-b8e2-4395-b615-3d016c6aa3d7.jpeg	2025-12-15 09:46:35.304887+00	114.10.100.10	\N	attendances/39/check_out/2025-12-15/8fb9c820-9bea-4b45-b69d-9ce1f33967cd.jpeg	2025-12-15 04:53:19.065583+00	2025-12-15 09:46:36.120365+00	-5.38758730	105.28016550	Jalan Alam Cantik, Kalibalau Kencana, Bandar Lampung, Lampung, Sumatra, 35133, Indonesia	-5.38758260	105.28014730	Jalan Alam Kurnia, Kalibalau Kencana, Bandar Lampung, Lampung, Sumatra, 35133, Indonesia	0.00
1083	50	23	2025-12-15	absent	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	2025-12-15 16:00:01.201118+00	2025-12-15 16:00:01.201124+00	\N	\N	\N	\N	\N	\N	\N
1087	40	28	2025-12-15	absent	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	2025-12-15 16:00:01.401537+00	2025-12-15 16:00:01.401543+00	\N	\N	\N	\N	\N	\N	\N
672	41	12	2025-12-02	present	2025-12-02 02:22:49.949652+00	2025-12-02 12:13:02.381673+00	9.84	41	2025-12-02 02:22:49.949652+00	114.10.100.168	Di dinas koperasi 	attendances/41/check_in/2025-12-02/74bd4570-2572-49e5-a739-cad35e341047.jpeg	2025-12-02 12:13:02.381673+00	103.105.82.245	\N	attendances/41/check_out/2025-12-02/dcfca47c-3f30-4b27-80a8-bed72bd97cc9.jpeg	2025-12-02 02:22:50.899207+00	2025-12-02 12:13:03.312944+00	-5.43356937	105.25869457	Jalan Cut Mutia, Sumur Batu, Bandar Lampung, Lampung, Sumatra, 35401, Indonesia	-5.38758811	105.28017389	Jalan Alam Cantik, Kalibalau Kencana, Bandar Lampung, Lampung, Sumatra, 35133, Indonesia	0.00
1080	14	28	2025-12-15	invalid	2025-12-15 11:56:27.280095+00	\N	\N	14	2025-12-15 11:56:27.280095+00	182.2.165.31	\N	attendances/14/check_in/2025-12-15/785bba22-4ed2-4de5-a432-3db573032673.jpeg	\N	\N	\N	\N	2025-12-15 11:56:28.41471+00	2025-12-15 16:30:00.072171+00	-6.18525830	106.82033830	Jalan Kampung Bali X, RW 09, Kampung Bali, Tanah Abang, Jakarta Pusat, Daerah Khusus Ibukota Jakarta, Jawa, 10250, Indonesia	\N	\N	\N	\N
1093	23	33	2025-12-16	present	2025-12-16 01:08:59.867292+00	2025-12-16 10:57:16.880116+00	9.80	23	2025-12-16 01:08:59.867292+00	103.105.82.243	\N	attendances/23/check_in/2025-12-16/ecbf90b6-3eee-4fcc-887e-7942f5a7fc47.jpeg	2025-12-16 10:57:16.880116+00	103.105.82.243	\N	attendances/23/check_out/2025-12-16/b7d0b897-36a4-4434-8c94-ccd849b14bfb.jpeg	2025-12-16 01:09:00.921981+00	2025-12-16 10:57:17.668227+00	-5.38757227	105.28016721	Jalan Alam Cantik, Kalibalau Kencana, Bandar Lampung, Lampung, Sumatra, 35133, Indonesia	-5.38757194	105.28016692	Jalan Alam Cantik, Kalibalau Kencana, Bandar Lampung, Lampung, Sumatra, 35133, Indonesia	0.00
689	13	10	2025-12-02	absent	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	2025-12-02 16:00:00.176625+00	2025-12-02 16:00:00.176629+00	\N	\N	\N	\N	\N	\N	\N
1114	59	29	2025-12-16	absent	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	2025-12-16 16:00:00.245093+00	2025-12-16 16:00:00.245098+00	\N	\N	\N	\N	\N	\N	\N
1118	40	28	2025-12-16	absent	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	2025-12-16 16:00:00.323716+00	2025-12-16 16:00:00.323722+00	\N	\N	\N	\N	\N	\N	\N
1123	60	29	2025-12-17	present	2025-12-17 01:06:06.991609+00	2025-12-17 09:48:24.269574+00	8.70	60	2025-12-17 01:06:06.991609+00	103.145.34.18	\N	attendances/60/check_in/2025-12-17/c1d24621-393b-4c62-842c-123687f5bd30.jpeg	2025-12-17 09:48:24.269574+00	114.10.102.78	\N	attendances/60/check_out/2025-12-17/fcc13409-d338-4d83-841f-175b91fd793b.jpeg	2025-12-17 01:06:07.952336+00	2025-12-17 09:48:25.143023+00	-5.42568820	104.73793900	Kota Dalam, Tanggamus, Lampung, Sumatra, Indonesia	-5.42568700	104.73794570	Kota Dalam, Tanggamus, Lampung, Sumatra, Indonesia	0.00
1124	23	33	2025-12-17	present	2025-12-17 01:18:24.944203+00	2025-12-17 13:33:51.507548+00	12.26	23	2025-12-17 01:18:24.944203+00	103.105.82.243	\N	attendances/23/check_in/2025-12-17/bf885166-e668-4fc9-80fb-f08a29201388.jpeg	2025-12-17 13:33:51.507548+00	140.213.113.161	\N	attendances/23/check_out/2025-12-17/dc2306d6-6bcd-4612-bfab-a1bdadc56719.jpeg	2025-12-17 01:18:26.092783+00	2025-12-17 13:33:52.313057+00	-5.38757179	105.28016672	Jalan Alam Cantik, Kalibalau Kencana, Bandar Lampung, Lampung, Sumatra, 35133, Indonesia	-5.38759802	105.28018696	Jalan Alam Cantik, Kalibalau Kencana, Bandar Lampung, Lampung, Sumatra, 35133, Indonesia	0.00
1129	53	25	2025-12-17	present	2025-12-17 02:02:10.495908+00	2025-12-17 13:52:54.528132+00	11.85	53	2025-12-17 02:02:10.495908+00	103.87.231.107	\N	attendances/53/check_in/2025-12-17/1774634d-b763-4ba7-9ffb-683e74bf3d9c.jpeg	2025-12-17 13:52:54.528132+00	114.10.100.206	\N	attendances/53/check_out/2025-12-17/e9188e51-c2e2-41fd-b979-61dcde82ab28.jpg	2025-12-17 02:02:11.430661+00	2025-12-17 13:52:55.746867+00	-5.02824150	104.30403200	Jalan Raya Serengit, Mekar Sari, Lampung Barat, Lampung, Sumatra, Indonesia	-5.03595840	104.30396170	Lampung Barat, Lampung, Sumatra, Indonesia	0.00
642	41	12	2025-12-01	present	2025-12-01 02:42:09.699885+00	2025-12-01 11:05:54.973784+00	8.40	41	2025-12-01 02:42:09.699885+00	103.105.82.245	\N	attendances/41/check_in/2025-12-01/f5dabc4c-ec36-4d64-a92a-062e08b9daaf.jpeg	2025-12-01 11:05:54.973784+00	103.105.82.245	\N	attendances/41/check_out/2025-12-01/f6362296-9ad4-483a-8f40-0310d4cbcfa7.jpeg	2025-12-01 02:42:10.625858+00	2025-12-01 11:05:56.039774+00	-0.78927500	113.92132700	Kapuas, Kalimantan Tengah, Kalimantan, Indonesia	-5.38759153	105.28017375	Jalan Alam Cantik, Kalibalau Kencana, Bandar Lampung, Lampung, Sumatra, 35133, Indonesia	0.00
637	22	15	2025-12-01	present	2025-12-01 01:35:29.04571+00	2025-12-01 11:06:33.019758+00	9.52	22	2025-12-01 01:35:29.04571+00	103.105.82.245	\N	attendances/22/check_in/2025-12-01/722af874-8905-4a90-9188-52cf02617a09.jpeg	2025-12-01 11:06:33.019758+00	103.105.82.245	\N	attendances/22/check_out/2025-12-01/4ca6dfe2-6616-4927-94a0-14a93e9cec22.jpeg	2025-12-01 01:35:30.768986+00	2025-12-01 11:06:33.715781+00	-5.38758010	105.28016680	Jalan Alam Cantik, Kalibalau Kencana, Bandar Lampung, Lampung, Sumatra, 35133, Indonesia	-5.37694320	105.26776770	Perumnas Way Halim, Bandar Lampung, Lampung, Sumatra, 35132, Indonesia	0.00
1075	24	31	2025-12-15	present	2025-12-15 03:02:54.937043+00	2025-12-15 10:04:32.260928+00	7.03	24	2025-12-15 03:02:54.937043+00	103.105.82.243	\N	attendances/24/check_in/2025-12-15/d28ed634-46b1-4097-8414-e57389fcac7f.jpeg	2025-12-15 10:04:32.260928+00	103.105.82.243	\N	attendances/24/check_out/2025-12-15/b3704e14-a3a5-4f24-b859-621ff6281080.jpeg	2025-12-15 03:02:55.663085+00	2025-12-15 10:04:36.972626+00	-5.38758160	105.28016210	Jalan Alam Cantik, Kalibalau Kencana, Bandar Lampung, Lampung, Sumatra, 35133, Indonesia	-5.38756770	105.28013370	Jalan Alam Kurnia, Kalibalau Kencana, Bandar Lampung, Lampung, Sumatra, 35133, Indonesia	0.00
1082	59	29	2025-12-15	absent	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	2025-12-15 16:00:01.126746+00	2025-12-15 16:00:01.126751+00	\N	\N	\N	\N	\N	\N	\N
1086	20	31	2025-12-15	absent	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	2025-12-15 16:00:01.34322+00	2025-12-15 16:00:01.343225+00	\N	\N	\N	\N	\N	\N	\N
1092	58	27	2025-12-16	present	2025-12-16 01:02:16.826748+00	2025-12-16 09:17:55.045527+00	8.26	58	2025-12-16 01:02:16.826748+00	180.242.4.50	\N	attendances/58/check_in/2025-12-16/f49045e3-d51d-4bb1-a7f8-3aed4bb75801.jpeg	2025-12-16 09:17:55.045527+00	180.242.4.50	\N	attendances/58/check_out/2025-12-16/0cce844a-9436-46e4-af9f-cce80dc17fd6.jpeg	2025-12-16 01:02:17.958686+00	2025-12-16 09:17:56.418182+00	-4.05597200	103.29772360	Rantau Unji, Dempo Tengah, Pagar Alam, Sumatera Selatan, Sumatra, Indonesia	-4.05606590	103.29806890	Rantau Unji, Dempo Tengah, Pagar Alam, Sumatera Selatan, Sumatra, Indonesia	0.00
1094	49	23	2025-12-16	present	2025-12-16 01:10:40.387553+00	2025-12-16 10:09:10.587331+00	8.98	49	2025-12-16 01:10:40.387553+00	103.59.44.25	\N	attendances/49/check_in/2025-12-16/b412dd24-3063-4028-a8fb-0a0e8c7b66b7.jpeg	2025-12-16 10:09:10.587331+00	103.59.44.25	\N	attendances/49/check_out/2025-12-16/baf1ee5d-bf2c-428f-8ea2-282b16170a10.jpeg	2025-12-16 01:10:41.204364+00	2025-12-16 10:09:11.442677+00	-5.43049170	104.73907460	Gisting Bawah, Tanggamus, Lampung, Sumatra, Indonesia	-5.43049290	104.73907010	Gisting Bawah, Tanggamus, Lampung, Sumatra, Indonesia	0.00
665	39	17	2025-12-01	hybrid	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	2025-12-01 16:00:00.88454+00	2025-12-01 16:00:00.884544+00	\N	\N	\N	\N	\N	\N	\N
666	43	17	2025-12-01	hybrid	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	2025-12-01 16:00:00.893676+00	2025-12-01 16:00:00.89368+00	\N	\N	\N	\N	\N	\N	\N
671	40	11	2025-12-02	present	2025-12-02 02:08:01.113497+00	2025-12-02 09:26:05.754782+00	7.30	40	2025-12-02 02:08:01.113497+00	103.105.82.245	\N	attendances/40/check_in/2025-12-02/e4a4098b-ea71-4b04-88f1-f9bdd080e7b4.jpeg	2025-12-02 09:26:05.754782+00	103.105.82.245	\N	attendances/40/check_out/2025-12-02/6139723d-c1c0-4333-993c-0792c15ce857.jpeg	2025-12-02 02:08:01.954463+00	2025-12-02 09:26:07.527465+00	-5.37694320	105.26776770	Perumnas Way Halim, Bandar Lampung, Lampung, Sumatra, 35132, Indonesia	-5.37694320	105.26776770	Perumnas Way Halim, Bandar Lampung, Lampung, Sumatra, 35132, Indonesia	0.00
676	39	17	2025-12-02	present	2025-12-02 09:36:16.840901+00	2025-12-02 09:36:25.58125+00	0.00	39	2025-12-02 09:36:16.840901+00	103.105.82.245	\N	attendances/39/check_in/2025-12-02/388c9273-34e1-44c1-b2ad-dff260b202bc.jpeg	2025-12-02 09:36:25.58125+00	103.105.82.245	\N	attendances/39/check_out/2025-12-02/0ff6a5ad-b951-45b9-9eb9-a4a2acbced61.jpeg	2025-12-02 09:36:17.808495+00	2025-12-02 09:36:26.327168+00	-5.38759320	105.28015970	Jalan Alam Kurnia, Kalibalau Kencana, Bandar Lampung, Lampung, Sumatra, 35133, Indonesia	-5.38759320	105.28015970	Jalan Alam Kurnia, Kalibalau Kencana, Bandar Lampung, Lampung, Sumatra, 35133, Indonesia	0.00
668	42	11	2025-12-02	present	2025-12-02 01:56:31.277984+00	2025-12-02 10:05:13.315478+00	8.15	42	2025-12-02 01:56:31.277984+00	103.105.82.245	\N	attendances/42/check_in/2025-12-02/1f81390e-9f45-4764-ba06-c87f6f9cdc5b.jpeg	2025-12-02 10:05:13.315478+00	103.105.82.245	\N	attendances/42/check_out/2025-12-02/331c7caf-1f14-44cc-9166-cb628dbfde9d.jpeg	2025-12-02 01:56:32.002904+00	2025-12-02 10:05:14.250154+00	-5.38759280	105.28015710	Jalan Alam Kurnia, Kalibalau Kencana, Bandar Lampung, Lampung, Sumatra, 35133, Indonesia	-5.38760790	105.28014590	Jalan Alam Kurnia, Kalibalau Kencana, Bandar Lampung, Lampung, Sumatra, 35133, Indonesia	0.00
673	44	17	2025-12-02	present	2025-12-02 02:53:20.167213+00	2025-12-02 11:16:02.165097+00	8.38	44	2025-12-02 02:53:20.167213+00	103.105.82.245	\N	attendances/44/check_in/2025-12-02/492ef0da-5eb2-4e53-948b-8c299bdf3202.jpeg	2025-12-02 11:16:02.165097+00	103.105.82.245	\N	attendances/44/check_out/2025-12-02/9b8b9cee-6c05-4227-8cb5-d2f99a047e07.jpeg	2025-12-02 02:53:21.006711+00	2025-12-02 11:16:03.075961+00	-5.38757930	105.28016150	Jalan Alam Cantik, Kalibalau Kencana, Bandar Lampung, Lampung, Sumatra, 35133, Indonesia	-5.38765770	105.28013980	Jalan Alam Kurnia, Kalibalau Kencana, Bandar Lampung, Lampung, Sumatra, 35133, Indonesia	0.00
674	20	14	2025-12-02	present	2025-12-02 03:32:27.643269+00	2025-12-02 12:41:47.43355+00	9.16	20	2025-12-02 03:32:27.643269+00	103.105.82.245	\N	attendances/20/check_in/2025-12-02/393b57c0-ac7d-4a6a-ae9f-8e31191e4337.jpeg	2025-12-02 12:41:47.43355+00	114.10.101.67	\N	attendances/20/check_out/2025-12-02/ea4427d0-8856-4854-8328-b49c444f5a8f.jpeg	2025-12-02 03:32:28.519806+00	2025-12-02 12:41:48.193719+00	-5.38754500	105.28020200	Jalan Alam Cantik, Kalibalau Kencana, Bandar Lampung, Lampung, Sumatra, 35133, Indonesia	-4.89410000	105.21470000	Cak Mus, Jalan Lintas Sumatera, Terbanggi Besar, Lampung Tengah, Lampung, Sumatra, 34162, Indonesia	0.00
1096	50	23	2025-12-16	present	2025-12-16 01:13:13.364421+00	2025-12-16 10:51:25.118759+00	9.64	50	2025-12-16 01:13:13.364421+00	114.10.100.108	\N	attendances/50/check_in/2025-12-16/b3da75c6-4a73-406c-95ea-5f431e60bc77.jpeg	2025-12-16 10:51:25.118759+00	114.10.100.55	\N	attendances/50/check_out/2025-12-16/bf1dab3e-57fc-4f35-8cdf-2a4ca78ed987.jpeg	2025-12-16 01:13:14.116232+00	2025-12-16 10:51:25.860116+00	-5.42901520	104.73404680	Gisting Bawah, Tanggamus, Lampung, Sumatra, Indonesia	-5.42972640	104.73428520	Gisting Bawah, Tanggamus, Lampung, Sumatra, Indonesia	0.00
691	15	12	2025-12-02	absent	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	2025-12-02 16:00:00.188776+00	2025-12-02 16:00:00.188781+00	\N	\N	\N	\N	\N	\N	\N
696	43	17	2025-12-02	hybrid	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	2025-12-02 16:00:00.224322+00	2025-12-02 16:00:00.224329+00	\N	\N	\N	\N	\N	\N	\N
670	22	15	2025-12-02	invalid	2025-12-02 02:06:21.154651+00	\N	\N	22	2025-12-02 02:06:21.154651+00	103.105.82.245	\N	attendances/22/check_in/2025-12-02/498fa748-c711-444f-a2e0-d8de9e05676d.jpeg	\N	\N	\N	\N	2025-12-02 02:06:22.197912+00	2025-12-02 16:30:00.034356+00	-5.37694320	105.26776770	Perumnas Way Halim, Bandar Lampung, Lampung, Sumatra, 35132, Indonesia	\N	\N	\N	\N
702	42	11	2025-12-03	present	2025-12-03 02:07:59.804607+00	2025-12-03 10:07:16.100959+00	7.99	42	2025-12-03 02:07:59.804607+00	103.105.82.245	\N	attendances/42/check_in/2025-12-03/fed17bc9-8e96-4a39-9938-e0b2c2f0c50f.jpeg	2025-12-03 10:07:16.100959+00	103.105.82.245	\N	attendances/42/check_out/2025-12-03/5e3b32db-dc26-4ab2-9e5d-d7dd8ce3fbc5.jpeg	2025-12-03 02:08:00.600681+00	2025-12-03 10:07:17.025663+00	-5.38758510	105.28016460	Jalan Alam Cantik, Kalibalau Kencana, Bandar Lampung, Lampung, Sumatra, 35133, Indonesia	-5.38758130	105.28015800	Jalan Alam Cantik, Kalibalau Kencana, Bandar Lampung, Lampung, Sumatra, 35133, Indonesia	0.00
697	20	14	2025-12-03	invalid	2025-12-03 01:52:57.146395+00	\N	\N	20	2025-12-03 01:52:57.146395+00	103.105.82.245	\N	attendances/20/check_in/2025-12-03/0f3e2a61-18e5-4b49-ac3f-0fa697032eab.jpeg	\N	\N	\N	\N	2025-12-03 01:52:58.421024+00	2025-12-03 16:30:00.05538+00	-5.41680000	105.28240000	Kedamaian, Bandar Lampung, Lampung, Sumatra, 35122, Indonesia	\N	\N	\N	\N
698	24	15	2025-12-03	invalid	2025-12-03 01:55:56.524653+00	\N	\N	24	2025-12-03 01:55:56.524653+00	103.105.82.245	\N	attendances/24/check_in/2025-12-03/4e7c7cb7-aa08-40e0-859d-bede80d55242.jpeg	\N	\N	\N	\N	2025-12-03 01:55:57.355658+00	2025-12-03 16:30:00.061412+00	-5.39243230	105.25606330	Sukamenanti, Bandar Lampung, Lampung, Sumatra, 35123, Indonesia	\N	\N	\N	\N
704	40	11	2025-12-03	present	2025-12-03 02:22:15.24169+00	2025-12-03 10:03:30.480874+00	7.69	40	2025-12-03 02:22:15.24169+00	103.105.82.245	\N	attendances/40/check_in/2025-12-03/c3b4b4d1-9225-451c-a606-ba95cd979f7b.jpeg	2025-12-03 10:03:30.480874+00	103.105.82.245	\N	attendances/40/check_out/2025-12-03/1ea0e121-35e5-4a43-a9e0-d928d8e274fa.jpeg	2025-12-03 02:22:16.048717+00	2025-12-03 10:03:31.840786+00	-5.39243230	105.25606330	Sukamenanti, Bandar Lampung, Lampung, Sumatra, 35123, Indonesia	-5.39243230	105.25606330	Sukamenanti, Bandar Lampung, Lampung, Sumatra, 35123, Indonesia	0.00
1097	45	21	2025-12-16	present	2025-12-16 01:19:49.633974+00	2025-12-16 10:28:10.55439+00	9.14	45	2025-12-16 01:19:49.633974+00	180.242.4.50	\N	attendances/45/check_in/2025-12-16/5a4432c6-51a2-4cd7-9cce-d423b1914585.jpeg	2025-12-16 10:28:10.55439+00	180.242.4.50	\N	attendances/45/check_out/2025-12-16/08464d00-695f-4593-a3bb-bbc04e088f3b.jpeg	2025-12-16 01:19:50.596397+00	2025-12-16 10:28:11.354792+00	-4.05604299	103.29811906	Rantau Unji, Dempo Tengah, Pagar Alam, Sumatera Selatan, Sumatra, Indonesia	-4.05604299	103.29811906	Rantau Unji, Dempo Tengah, Pagar Alam, Sumatera Selatan, Sumatra, Indonesia	0.00
735	39	17	2025-12-04	present	2025-12-04 05:11:50.124128+00	2025-12-04 13:50:02.285161+00	8.64	39	2025-12-04 05:11:50.124128+00	103.105.82.245	\N	attendances/39/check_in/2025-12-04/716d07b5-12da-4dc4-92c9-fce0f82f8871.jpeg	2025-12-04 13:50:02.285161+00	182.3.101.189	\N	attendances/39/check_out/2025-12-04/ee7d37b1-9918-4055-8f01-d9b398a97473.jpeg	2025-12-04 05:11:51.344462+00	2025-12-04 15:03:57.978056+00	-5.38758440	105.28016170	Jalan Alam Cantik, Kalibalau Kencana, Bandar Lampung, Lampung, Sumatra, 35133, Indonesia	-5.44117260	105.29601790	Jalan Perumahan Garuntang Lestari, Way Lunik, Bandar Lampung, Lampung, Sumatra, 35245, Indonesia	0.00
729	42	11	2025-12-04	present	2025-12-04 02:06:05.519821+00	2025-12-04 11:13:21.993019+00	9.12	42	2025-12-04 02:06:05.519821+00	103.105.82.245	\N	attendances/42/check_in/2025-12-04/a59f2691-6b5e-454e-a4f6-659e1b214b71.jpeg	2025-12-04 11:13:21.993019+00	182.3.104.136	\N	attendances/42/check_out/2025-12-04/415216b0-5b6f-40ae-98f5-0a95bb75d961.jpeg	2025-12-04 02:06:06.287165+00	2025-12-04 15:03:57.985366+00	-5.38758250	105.28016150	Jalan Alam Cantik, Kalibalau Kencana, Bandar Lampung, Lampung, Sumatra, 35133, Indonesia	-5.38480770	105.28146380	Kalibalau Kencana, Bandar Lampung, Lampung, Sumatra, 35133, Indonesia	0.00
720	13	10	2025-12-03	absent	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	2025-12-03 16:00:00.577823+00	2025-12-03 16:00:00.577826+00	\N	\N	\N	\N	\N	\N	\N
1115	48	23	2025-12-16	absent	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	2025-12-16 16:00:00.277148+00	2025-12-16 16:00:00.277153+00	\N	\N	\N	\N	\N	\N	\N
1119	39	32	2025-12-16	hybrid	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	2025-12-16 16:00:00.333929+00	2025-12-16 16:00:00.333934+00	\N	\N	\N	\N	\N	\N	\N
732	41	12	2025-12-04	invalid	2025-12-04 02:41:56.047027+00	\N	\N	41	2025-12-04 02:41:56.047027+00	103.105.82.245	\N	attendances/41/check_in/2025-12-04/4341fde8-a1d3-4fec-be5d-989c27a78a90.jpeg	\N	\N	\N	\N	2025-12-04 02:41:56.915619+00	2025-12-04 16:30:00.013588+00	-5.38758419	105.28017874	Jalan Alam Cantik, Kalibalau Kencana, Bandar Lampung, Lampung, Sumatra, 35133, Indonesia	\N	\N	\N	\N
733	15	12	2025-12-04	invalid	2025-12-04 02:44:46.704849+00	\N	\N	15	2025-12-04 02:44:46.704849+00	103.105.82.245	\N	attendances/15/check_in/2025-12-04/153d8e0c-bcc7-4f99-b345-fb02a23ae968.jpeg	\N	\N	\N	\N	2025-12-04 02:44:47.714842+00	2025-12-04 16:30:00.014655+00	-5.38758380	105.28011870	Jalan Alam Kurnia, Kalibalau Kencana, Bandar Lampung, Lampung, Sumatra, 35133, Indonesia	\N	\N	\N	\N
1122	58	27	2025-12-17	present	2025-12-17 01:05:11.619326+00	2025-12-17 09:17:39.915504+00	8.21	58	2025-12-17 01:05:11.619326+00	180.242.4.50	\N	attendances/58/check_in/2025-12-17/29c9d883-6126-48e8-ada2-21b9191d62af.jpeg	2025-12-17 09:17:39.915504+00	180.242.4.50	\N	attendances/58/check_out/2025-12-17/cb0a48c8-3129-45e6-a0e2-7d6d8bc5b2c0.jpeg	2025-12-17 01:05:12.63157+00	2025-12-17 09:17:40.910762+00	-4.05602040	103.29797080	Rantau Unji, Dempo Tengah, Pagar Alam, Sumatera Selatan, Sumatra, Indonesia	-4.05607420	103.29806260	Rantau Unji, Dempo Tengah, Pagar Alam, Sumatera Selatan, Sumatra, Indonesia	0.00
1121	61	29	2025-12-17	present	2025-12-17 00:09:52.103192+00	2025-12-17 10:13:18.500601+00	10.06	61	2025-12-17 00:09:52.103192+00	114.10.102.3	Persiapan Lokasi transit kohe 	attendances/61/check_in/2025-12-17/a066de23-b08c-4503-b92f-be196cd1b444.jpeg	2025-12-17 10:13:18.500601+00	114.10.102.3	\N	attendances/61/check_out/2025-12-17/b358f09d-81ef-48ae-93d5-2ae440daa679.jpeg	2025-12-17 00:09:53.636697+00	2025-12-17 10:13:19.627287+00	-5.05129760	104.10744080	Gang Buntu, Liwa, Lampung Barat, Lampung, Sumatra, 34812, Indonesia	-5.05030250	104.10501630	Jalan Sutoyo, Liwa, Lampung Barat, Lampung, Sumatra, 34812, Indonesia	0.00
1130	24	31	2025-12-17	present	2025-12-17 02:02:28.572478+00	2025-12-17 10:40:46.53542+00	8.64	24	2025-12-17 02:02:28.572478+00	103.105.82.243	\N	attendances/24/check_in/2025-12-17/de8a0a2d-1eb1-4fc9-9d31-32b30c68f4c4.jpeg	2025-12-17 10:40:46.53542+00	103.105.82.243	\N	attendances/24/check_out/2025-12-17/45efa9b9-3833-4da2-b99e-17a1db9eeac8.jpeg	2025-12-17 02:02:29.433022+00	2025-12-17 10:40:47.571274+00	-5.38757080	105.28017870	Jalan Alam Cantik, Kalibalau Kencana, Bandar Lampung, Lampung, Sumatra, 35133, Indonesia	-5.37820700	105.27800970	Masjid Daarul Ukhuwah, Perumnas Way Halim, Way Halim Permai, Bandar Lampung, Lampung, Sumatra, 35133, Indonesia	0.00
1131	62	30	2025-12-17	invalid	2025-12-17 02:03:12.070589+00	\N	\N	62	2025-12-17 02:03:12.070589+00	110.137.36.58	\N	attendances/62/check_in/2025-12-17/107e53a1-f453-496c-aee4-0774114d3e21.jpeg	\N	\N	\N	\N	2025-12-17 02:03:12.83458+00	2025-12-17 16:30:00.062515+00	-5.40129930	105.23241060	Jalan Kepodang, Suka Jawa, Bandar Lampung, Lampung, Sumatra, 35151, Indonesia	\N	\N	\N	\N
705	44	17	2025-12-03	present	2025-12-03 03:01:51.772318+00	2025-12-03 10:31:22.528103+00	7.49	44	2025-12-03 03:01:51.772318+00	114.10.100.218	\N	attendances/44/check_in/2025-12-03/4719d9be-0b17-4eab-9d31-31b4aaf1c97f.jpeg	2025-12-03 10:31:22.528103+00	103.105.82.245	\N	attendances/44/check_out/2025-12-03/92b76aa3-657c-416c-9518-9280d7e5dcdb.jpeg	2025-12-03 03:01:52.704775+00	2025-12-03 10:31:23.677949+00	-5.36186200	105.24377580	Fakultas Ekonomi dan Bisnis Universitas Lampung, Gang M. Said, Sepang Jaya, Bandar Lampung, Lampung, Sumatra, 35141, Indonesia	-5.38758320	105.28016180	Jalan Alam Cantik, Kalibalau Kencana, Bandar Lampung, Lampung, Sumatra, 35133, Indonesia	0.00
699	23	15	2025-12-03	present	2025-12-03 02:00:14.371981+00	2025-12-03 11:26:30.417728+00	9.44	23	2025-12-03 02:00:14.371981+00	182.3.101.181	\N	attendances/23/check_in/2025-12-03/fe86200d-993b-427c-91c6-b5847ee6d42f.jpeg	2025-12-03 11:26:30.417728+00	103.105.82.245	\N	attendances/23/check_out/2025-12-03/239b252c-1190-4bcd-af96-abafa5cc699a.jpeg	2025-12-03 02:00:15.441657+00	2025-12-03 11:26:31.514689+00	-5.38754735	105.28018205	Jalan Alam Cantik, Kalibalau Kencana, Bandar Lampung, Lampung, Sumatra, 35133, Indonesia	-5.38754735	105.28018205	Jalan Alam Cantik, Kalibalau Kencana, Bandar Lampung, Lampung, Sumatra, 35133, Indonesia	0.00
1111	44	34	2025-12-16	present	2025-12-16 03:13:47.596861+00	2025-12-16 12:27:52.347369+00	9.23	44	2025-12-16 03:13:47.596861+00	103.105.82.243	\N	attendances/44/check_in/2025-12-16/4802181e-007f-4f80-9367-9241b474bf4c.jpeg	2025-12-16 12:27:52.347369+00	114.10.102.201	\N	attendances/44/check_out/2025-12-16/f9c85303-3710-48ea-9b0a-94c865d991bd.jpeg	2025-12-16 03:13:48.601653+00	2025-12-16 12:27:53.622916+00	-5.38758520	105.28015390	Jalan Alam Kurnia, Kalibalau Kencana, Bandar Lampung, Lampung, Sumatra, 35133, Indonesia	-5.37281900	105.24939040	Gang Zakaria III, Sepang Jaya, Bandar Lampung, Lampung, Sumatra, 35148, Indonesia	0.00
734	20	14	2025-12-04	invalid	2025-12-04 03:22:57.894795+00	\N	\N	20	2025-12-04 03:22:57.894795+00	114.10.68.65	\N	attendances/20/check_in/2025-12-04/e5ce902f-e988-4f2a-a71a-adb84c584e27.jpeg	\N	\N	\N	\N	2025-12-04 03:22:58.793484+00	2025-12-04 16:30:00.015483+00	-5.38377302	105.28154051	Kalibalau Kencana, Bandar Lampung, Lampung, Sumatra, 35133, Indonesia	\N	\N	\N	\N
1113	46	21	2025-12-16	absent	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	2025-12-16 16:00:00.189185+00	2025-12-16 16:00:00.189191+00	\N	\N	\N	\N	\N	\N	\N
1117	20	31	2025-12-16	absent	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	2025-12-16 16:00:00.315338+00	2025-12-16 16:00:00.315344+00	\N	\N	\N	\N	\N	\N	\N
706	39	17	2025-12-03	present	2025-12-03 10:58:12.123966+00	2025-12-03 10:58:21.199296+00	0.00	39	2025-12-03 10:58:12.123966+00	103.105.82.245	\N	attendances/39/check_in/2025-12-03/173cedca-f326-41ba-bc25-a6c0a0711a86.jpeg	2025-12-03 10:58:21.199296+00	103.105.82.245	\N	attendances/39/check_out/2025-12-03/7f14ad62-3582-40da-b787-64d73cb78eef.jpeg	2025-12-03 10:58:12.957427+00	2025-12-03 10:58:21.975771+00	-5.38758250	105.28016100	Jalan Alam Cantik, Kalibalau Kencana, Bandar Lampung, Lampung, Sumatra, 35133, Indonesia	-5.38758250	105.28016100	Jalan Alam Cantik, Kalibalau Kencana, Bandar Lampung, Lampung, Sumatra, 35133, Indonesia	0.00
707	15	12	2025-12-03	present	2025-12-03 13:38:10.137909+00	2025-12-03 13:38:22.332131+00	0.00	15	2025-12-03 13:38:10.137909+00	182.253.63.50	\N	attendances/15/check_in/2025-12-03/1ea3cffe-ddc2-4931-ace4-97e10917591e.jpeg	2025-12-03 13:38:22.332131+00	182.253.63.50	Lupa	attendances/15/check_out/2025-12-03/930c774d-0eea-4f0f-95a5-d9e3b79233e6.jpeg	2025-12-03 13:38:11.518957+00	2025-12-03 13:38:24.088494+00	-5.39569790	105.32384000	Lampung Selatan, Lampung, Sumatra, 35131, Indonesia	-5.39569790	105.32384000	Lampung Selatan, Lampung, Sumatra, 35131, Indonesia	0.00
731	44	17	2025-12-04	present	2025-12-04 02:37:58.2575+00	2025-12-04 11:44:01.406354+00	9.10	44	2025-12-04 02:37:58.2575+00	103.105.82.245	\N	attendances/44/check_in/2025-12-04/018ed46b-e753-4787-acbf-09530147e856.jpeg	2025-12-04 11:44:01.406354+00	114.10.102.179	\N	attendances/44/check_out/2025-12-04/65769266-794b-41ef-bd66-25a7bbf87a20.jpeg	2025-12-04 02:37:59.021006+00	2025-12-04 15:03:58.006942+00	-5.38758190	105.28015880	Jalan Alam Cantik, Kalibalau Kencana, Bandar Lampung, Lampung, Sumatra, 35133, Indonesia	-5.38758830	105.28018310	Jalan Alam Cantik, Kalibalau Kencana, Bandar Lampung, Lampung, Sumatra, 35133, Indonesia	0.00
1098	63	25	2025-12-16	invalid	2025-12-16 01:28:23.22228+00	\N	\N	63	2025-12-16 01:28:23.22228+00	103.87.231.107	\N	attendances/63/check_in/2025-12-16/87403dbf-a1dd-4704-a3b1-9e277abd79a1.jpeg	\N	\N	\N	\N	2025-12-16 01:28:24.292045+00	2025-12-16 16:30:00.04281+00	-5.02816620	104.30402540	Jalan Raya Serengit, Mekar Sari, Lampung Barat, Lampung, Sumatra, Indonesia	\N	\N	\N	\N
1107	62	30	2025-12-16	invalid	2025-12-16 02:37:17.736075+00	\N	\N	62	2025-12-16 02:37:17.736075+00	182.3.103.142	\N	attendances/62/check_in/2025-12-16/a6949d57-b761-4b95-b7b6-75a74931884c.jpeg	\N	\N	\N	\N	2025-12-16 02:37:18.49721+00	2025-12-16 16:30:00.060132+00	-5.38757670	105.28014250	Jalan Alam Kurnia, Kalibalau Kencana, Bandar Lampung, Lampung, Sumatra, 35133, Indonesia	\N	\N	\N	\N
726	43	17	2025-12-03	hybrid	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	2025-12-03 16:00:00.609899+00	2025-12-03 16:00:00.609904+00	\N	\N	\N	\N	\N	\N	\N
700	22	15	2025-12-03	invalid	2025-12-03 02:00:29.586605+00	\N	\N	22	2025-12-03 02:00:29.586605+00	103.130.18.46	\N	attendances/22/check_in/2025-12-03/91d63b55-aefe-416d-82ac-48b00c703a95.jpeg	\N	\N	\N	\N	2025-12-03 02:00:30.357826+00	2025-12-03 16:30:00.062297+00	-5.36018500	105.24746850	Sepang Jaya, Bandar Lampung, Lampung, Sumatra, 35141, Indonesia	\N	\N	\N	\N
701	14	11	2025-12-03	invalid	2025-12-03 02:03:09.356527+00	\N	\N	14	2025-12-03 02:03:09.356527+00	103.105.82.245	\N	attendances/14/check_in/2025-12-03/ffb11da8-b289-476a-b5e8-c5935dcb82fc.jpeg	\N	\N	\N	\N	2025-12-03 02:03:10.157883+00	2025-12-03 16:30:00.064319+00	-5.39243230	105.25606330	Sukamenanti, Bandar Lampung, Lampung, Sumatra, 35123, Indonesia	\N	\N	\N	\N
703	41	12	2025-12-03	invalid	2025-12-03 02:20:23.411316+00	\N	\N	41	2025-12-03 02:20:23.411316+00	103.105.82.245	\N	attendances/41/check_in/2025-12-03/4a82cc9d-dd37-45d2-801e-950515e19959.jpeg	\N	\N	\N	\N	2025-12-03 02:20:24.447342+00	2025-12-03 16:30:00.065385+00	-5.38758577	105.28017581	Jalan Alam Cantik, Kalibalau Kencana, Bandar Lampung, Lampung, Sumatra, 35133, Indonesia	\N	\N	\N	\N
1128	52	24	2025-12-17	present	2025-12-17 01:55:00.311374+00	2025-12-17 10:01:02.642651+00	8.10	52	2025-12-17 01:55:00.311374+00	114.10.100.111	Nyari kayu untuk patok gudang baru	attendances/52/check_in/2025-12-17/5658e348-5b76-4e27-87b7-b4a037ff75bf.jpeg	2025-12-17 10:01:02.642651+00	114.10.100.111	\N	attendances/52/check_out/2025-12-17/e5cecad4-619d-4579-803a-1f6c621bba3c.jpeg	2025-12-17 01:55:01.179299+00	2025-12-17 10:01:03.805569+00	-5.04901760	104.30953910	Sekincau, Lampung Barat, Lampung, Sumatra, Indonesia	-5.02823240	104.30404710	Jalan Raya Serengit, Mekar Sari, Lampung Barat, Lampung, Sumatra, Indonesia	0.00
1127	54	25	2025-12-17	present	2025-12-17 01:50:38.744405+00	2025-12-17 10:05:50.243284+00	8.25	54	2025-12-17 01:50:38.744405+00	103.87.231.107	\N	attendances/54/check_in/2025-12-17/b4a3a0e2-064f-4501-9976-640e4c79ec9b.jpeg	2025-12-17 10:05:50.243284+00	103.87.231.107	\N	attendances/54/check_out/2025-12-17/5205b800-0688-43c2-b237-9688257dd354.jpeg	2025-12-17 01:50:39.825695+00	2025-12-17 10:05:51.187273+00	-5.02822980	104.30404590	Jalan Raya Serengit, Mekar Sari, Lampung Barat, Lampung, Sumatra, Indonesia	-5.02823020	104.30404580	Jalan Raya Serengit, Mekar Sari, Lampung Barat, Lampung, Sumatra, Indonesia	0.00
1125	49	23	2025-12-17	present	2025-12-17 01:20:01.109865+00	2025-12-17 10:34:52.247837+00	9.25	49	2025-12-17 01:20:01.109865+00	103.59.44.25	\N	attendances/49/check_in/2025-12-17/0812b5b3-4e46-4dbb-ae87-306ffc663468.jpeg	2025-12-17 10:34:52.247837+00	103.59.44.25	\N	attendances/49/check_out/2025-12-17/4f656685-0fad-47ae-9789-8788ee09abca.jpeg	2025-12-17 01:20:01.861415+00	2025-12-17 10:34:53.05231+00	-5.43049030	104.73912890	Gisting Bawah, Tanggamus, Lampung, Sumatra, Indonesia	-5.43060100	104.73920570	Gisting Bawah, Tanggamus, Lampung, Sumatra, Indonesia	0.00
1126	51	23	2025-12-17	present	2025-12-17 01:25:08.162543+00	2025-12-17 10:57:12.112216+00	9.53	51	2025-12-17 01:25:08.162543+00	182.3.104.58	\N	attendances/51/check_in/2025-12-17/3e855e2c-957e-4620-aef4-e5fcf36fd084.jpeg	2025-12-17 10:57:12.112216+00	103.59.44.25	\N	attendances/51/check_out/2025-12-17/649b68ec-a2ba-407f-9b01-6e025da0e6f3.jpeg	2025-12-17 01:25:09.19071+00	2025-12-17 10:57:12.814828+00	-5.43048870	104.73907800	Gisting Bawah, Tanggamus, Lampung, Sumatra, Indonesia	-5.43039810	104.73902920	Gisting Bawah, Tanggamus, Lampung, Sumatra, Indonesia	0.00
728	23	15	2025-12-04	present	2025-12-04 02:04:49.236389+00	2025-12-04 14:14:26.310523+00	12.16	23	2025-12-04 02:04:49.236389+00	103.105.82.245	\N	attendances/23/check_in/2025-12-04/b515a302-2220-479c-b78e-9f5383e60a45.jpeg	2025-12-04 14:14:26.310523+00	140.213.112.82	\N	attendances/23/check_out/2025-12-04/2c79efc2-7cd8-4a66-acba-91c1e761dd71.jpeg	2025-12-04 02:04:50.257147+00	2025-12-04 15:03:57.877859+00	-5.38756175	105.28017745	Jalan Alam Cantik, Kalibalau Kencana, Bandar Lampung, Lampung, Sumatra, 35133, Indonesia	-5.38758629	105.28013748	Jalan Alam Kurnia, Kalibalau Kencana, Bandar Lampung, Lampung, Sumatra, 35133, Indonesia	0.00
736	14	11	2025-12-04	present	2025-12-04 09:52:52.601502+00	2025-12-04 10:13:20.699906+00	0.34	14	2025-12-04 09:52:52.601502+00	103.105.82.245	\N	attendances/14/check_in/2025-12-04/6fa50e1e-cd69-48d2-a68e-9323a7b2162f.jpeg	2025-12-04 10:13:20.699906+00	103.105.82.245	\N	attendances/14/check_out/2025-12-04/6033d511-1b29-4c66-b6f0-f030f9cf2aab.jpeg	2025-12-04 09:52:53.893186+00	2025-12-04 15:03:57.954932+00	-5.39243230	105.25606330	Sukamenanti, Bandar Lampung, Lampung, Sumatra, 35123, Indonesia	-5.39243230	105.25606330	Sukamenanti, Bandar Lampung, Lampung, Sumatra, 35123, Indonesia	0.00
730	40	11	2025-12-04	present	2025-12-04 02:23:37.658535+00	2025-12-04 10:20:57.312877+00	7.96	40	2025-12-04 02:23:37.658535+00	103.105.82.245	\N	attendances/40/check_in/2025-12-04/63f9b285-6da0-4afc-a04d-375de68dcaee.jpeg	2025-12-04 10:20:57.312877+00	103.105.82.245	\N	attendances/40/check_out/2025-12-04/bf45567d-6635-4f69-93d2-4dd65c9e267b.jpeg	2025-12-04 02:23:38.578922+00	2025-12-04 15:03:57.988986+00	-5.38761188	105.28015776	Jalan Alam Kurnia, Kalibalau Kencana, Bandar Lampung, Lampung, Sumatra, 35133, Indonesia	-5.38759582	105.28016672	Jalan Alam Kurnia, Kalibalau Kencana, Bandar Lampung, Lampung, Sumatra, 35133, Indonesia	0.00
1143	63	25	2025-12-17	present	2025-12-17 03:42:13.86498+00	2025-12-17 09:45:16.250209+00	6.05	63	2025-12-17 03:42:13.86498+00	114.10.100.36	Telat,,, ngurusin motor perkebunan	attendances/63/check_in/2025-12-17/aa0aec23-fada-4f54-b4ad-3d1586c72ac8.jpeg	2025-12-17 09:45:16.250209+00	103.87.231.107	\N	attendances/63/check_out/2025-12-17/81894aee-9a5b-4e49-9941-7f00eea060fa.jpeg	2025-12-17 03:42:14.964431+00	2025-12-17 09:45:17.336122+00	-5.02822620	104.30403950	Jalan Raya Serengit, Mekar Sari, Lampung Barat, Lampung, Sumatra, Indonesia	-5.02823030	104.30404560	Jalan Raya Serengit, Mekar Sari, Lampung Barat, Lampung, Sumatra, Indonesia	0.00
1132	44	34	2025-12-17	present	2025-12-17 02:07:32.76885+00	2025-12-17 10:24:33.871507+00	8.28	44	2025-12-17 02:07:32.76885+00	114.10.102.27	\N	attendances/44/check_in/2025-12-17/bb4c312b-987f-4abd-b6c8-945c9304319b.jpeg	2025-12-17 10:24:33.871507+00	103.105.82.243	\N	attendances/44/check_out/2025-12-17/57f01450-52cd-411b-bf0a-37591df1d1bb.jpeg	2025-12-17 02:07:33.894696+00	2025-12-17 10:24:34.58567+00	-5.37265330	105.24923170	Gang Zakaria III, Sepang Jaya, Bandar Lampung, Lampung, Sumatra, 35148, Indonesia	-5.38758020	105.28015100	Jalan Alam Kurnia, Kalibalau Kencana, Bandar Lampung, Lampung, Sumatra, 35133, Indonesia	0.00
1134	45	21	2025-12-17	present	2025-12-17 02:22:39.497608+00	2025-12-17 14:09:10.416383+00	11.78	45	2025-12-17 02:22:39.497608+00	182.1.228.99	\N	attendances/45/check_in/2025-12-17/581e19d7-780c-4759-a4b4-29ee16cc50ce.jpeg	2025-12-17 14:09:10.416383+00	182.1.237.239	\N	attendances/45/check_out/2025-12-17/bc3c7184-3012-459c-aedb-82a7fa47e211.jpeg	2025-12-17 02:22:40.553961+00	2025-12-17 14:09:11.503219+00	-4.05607100	103.29806660	Rantau Unji, Dempo Tengah, Pagar Alam, Sumatera Selatan, Sumatra, Indonesia	-4.05604299	103.29811906	Rantau Unji, Dempo Tengah, Pagar Alam, Sumatera Selatan, Sumatra, Indonesia	0.00
\.


--
-- Data for Name: guest_accounts; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.guest_accounts (id, user_id, guest_type, valid_from, valid_until, sponsor_id, notes, created_at, updated_at) FROM stdin;
2	34	intern	2025-11-03 17:00:00+00	2026-05-03 17:00:00+00	\N	Kontrak 	2025-11-05 09:09:19.867669+00	2025-12-04 14:23:11.563846+00
\.


--
-- Data for Name: job_executions; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.job_executions (id, job_id, started_at, finished_at, duration_seconds, success, message, error_trace, result_data, created_at, updated_at) FROM stdin;
1	auto_create_daily_attendance	2025-11-03 16:16:00.001787+00	2025-11-03 16:16:00.041113+00	0.039	t	Auto-create attendance selesai. Total: 28 karyawan, Created: 0, Skipped: 4, Errors: 24	\N	{"date": "2025-11-03", "total_employees": 28, "created": 0, "skipped": 4, "errors": 24}	2025-11-03 16:16:00.044019+00	2025-11-03 16:16:00.044023+00
2	auto_create_daily_attendance	2025-11-04 16:00:00.067754+00	2025-11-04 16:00:05.464353+00	5.397	t	Auto-create attendance selesai. Total: 25 karyawan, Created: 25, Skipped: 0, Errors: 0	\N	{"date": "2025-11-04", "total_employees": 25, "created": 25, "skipped": 0, "errors": 0}	2025-11-04 16:00:05.480081+00	2025-11-04 16:00:05.480088+00
3	mark_invalid_no_checkout	2025-11-04 16:59:00.001988+00	2025-11-04 16:59:00.019004+00	0.017	t	Mark invalid no checkout selesai. Total ditemukan: 0, Updated: 0, Errors: 0	\N	{"date": "2025-11-04", "total_found": 0, "updated": 0, "errors": 0}	2025-11-04 16:59:00.020076+00	2025-11-04 16:59:00.020082+00
4	auto_create_daily_attendance	2025-11-05 16:00:00.003024+00	2025-11-05 16:00:00.637195+00	0.634	t	Auto-create attendance selesai. Total: 31 karyawan, Created: 31, Skipped: 0, Errors: 0	\N	{"date": "2025-11-05", "total_employees": 31, "created": 31, "skipped": 0, "errors": 0}	2025-11-05 16:00:00.639419+00	2025-11-05 16:00:00.639423+00
5	mark_invalid_no_checkout	2025-11-05 16:59:00.002349+00	2025-11-05 16:59:00.015149+00	0.013	t	Mark invalid no checkout selesai. Total ditemukan: 0, Updated: 0, Errors: 0	\N	{"date": "2025-11-05", "total_found": 0, "updated": 0, "errors": 0}	2025-11-05 16:59:00.01606+00	2025-11-05 16:59:00.016064+00
6	auto_create_daily_attendance	2025-11-06 16:00:00.055836+00	2025-11-06 16:00:00.511664+00	0.456	t	Auto-create attendance selesai. Total: 31 karyawan, Created: 23, Skipped: 8, Errors: 0	\N	{"date": "2025-11-06", "total_employees": 31, "created": 23, "skipped": 8, "errors": 0}	2025-11-06 16:00:00.520378+00	2025-11-06 16:00:00.520384+00
7	mark_invalid_no_checkout	2025-11-06 16:59:00.004047+00	2025-11-06 16:59:00.12371+00	0.120	t	Mark invalid no checkout selesai. Total ditemukan: 4, Updated: 4, Errors: 0	\N	{"date": "2025-11-06", "total_found": 4, "updated": 4, "errors": 0}	2025-11-06 16:59:00.124543+00	2025-11-06 16:59:00.124545+00
8	auto_create_daily_attendance	2025-11-07 16:00:00.043948+00	2025-11-07 16:00:00.845723+00	0.802	t	Auto-create attendance selesai. Total: 30 karyawan, Created: 20, Skipped: 10, Errors: 0	\N	{"date": "2025-11-07", "total_employees": 30, "created": 20, "skipped": 10, "errors": 0}	2025-11-07 16:00:00.855021+00	2025-11-07 16:00:00.855028+00
9	mark_invalid_no_checkout	2025-11-07 16:59:00.004172+00	2025-11-07 16:59:00.073036+00	0.069	t	Mark invalid no checkout selesai. Total ditemukan: 4, Updated: 4, Errors: 0	\N	{"date": "2025-11-07", "total_found": 4, "updated": 4, "errors": 0}	2025-11-07 16:59:00.073892+00	2025-11-07 16:59:00.073895+00
10	auto_create_daily_attendance	2025-11-08 16:00:00.178149+00	2025-11-08 16:00:04.303173+00	4.125	t	Auto-create attendance selesai. Total: 30 karyawan, Created: 21, Skipped: 9, Errors: 0	\N	{"date": "2025-11-08", "total_employees": 30, "created": 21, "skipped": 9, "errors": 0}	2025-11-08 16:00:04.543406+00	2025-11-08 16:00:04.543414+00
11	mark_invalid_no_checkout	2025-11-08 16:59:00.005584+00	2025-11-08 16:59:00.061121+00	0.056	t	Mark invalid no checkout selesai. Total ditemukan: 4, Updated: 4, Errors: 0	\N	{"date": "2025-11-08", "total_found": 4, "updated": 4, "errors": 0}	2025-11-08 16:59:00.061834+00	2025-11-08 16:59:00.061836+00
12	auto_create_daily_attendance	2025-11-09 16:00:00.156523+00	2025-11-09 16:00:00.160128+00	0.004	t	Skip auto-create attendance untuk tanggal 2025-11-09 (hari Minggu bukan hari kerja)	\N	{"date": "2025-11-09", "skipped": true, "reason": "Sunday is not a working day"}	2025-11-09 16:00:00.361167+00	2025-11-09 16:00:00.361177+00
13	mark_invalid_no_checkout	2025-11-09 16:59:00.009824+00	2025-11-09 16:59:00.177001+00	0.167	t	Mark invalid no checkout selesai. Total ditemukan: 0, Updated: 0, Errors: 0	\N	{"date": "2025-11-09", "total_found": 0, "updated": 0, "errors": 0}	2025-11-09 16:59:00.17868+00	2025-11-09 16:59:00.178684+00
14	auto_create_daily_attendance	2025-11-10 16:00:00.063978+00	2025-11-10 16:00:00.899921+00	0.836	t	Auto-create attendance selesai. Total: 30 karyawan, Created: 21, Skipped: 9, Errors: 0	\N	{"date": "2025-11-10", "total_employees": 30, "created": 21, "skipped": 9, "errors": 0}	2025-11-10 16:00:00.913525+00	2025-11-10 16:00:00.913533+00
15	mark_invalid_no_checkout	2025-11-10 16:59:00.011322+00	2025-11-10 16:59:00.052797+00	0.041	t	Mark invalid no checkout selesai. Total ditemukan: 0, Updated: 0, Errors: 0	\N	{"date": "2025-11-10", "total_found": 0, "updated": 0, "errors": 0}	2025-11-10 16:59:00.054378+00	2025-11-10 16:59:00.054383+00
16	auto_create_daily_attendance	2025-11-11 16:00:00.113036+00	2025-11-11 16:00:01.333641+00	1.221	t	Auto-create attendance selesai. Total: 30 karyawan, Created: 21, Skipped: 9, Errors: 0	\N	{"date": "2025-11-11", "total_employees": 30, "created": 21, "skipped": 9, "errors": 0}	2025-11-11 16:00:01.348592+00	2025-11-11 16:00:01.348601+00
17	mark_invalid_no_checkout	2025-11-11 16:59:00.005079+00	2025-11-11 16:59:00.078857+00	0.074	t	Mark invalid no checkout selesai. Total ditemukan: 4, Updated: 4, Errors: 0	\N	{"date": "2025-11-11", "total_found": 4, "updated": 4, "errors": 0}	2025-11-11 16:59:00.079545+00	2025-11-11 16:59:00.079549+00
18	auto_create_daily_attendance	2025-11-12 16:00:00.166504+00	2025-11-12 16:00:02.608048+00	2.442	t	Auto-create attendance selesai. Total: 30 karyawan, Created: 19, Skipped: 11, Errors: 0	\N	{"date": "2025-11-12", "total_employees": 30, "created": 19, "skipped": 11, "errors": 0}	2025-11-12 16:00:02.644245+00	2025-11-12 16:00:02.644251+00
19	mark_invalid_no_checkout	2025-11-12 16:59:00.006409+00	2025-11-12 16:59:00.061025+00	0.055	t	Mark invalid no checkout selesai. Total ditemukan: 1, Updated: 1, Errors: 0	\N	{"date": "2025-11-12", "total_found": 1, "updated": 1, "errors": 0}	2025-11-12 16:59:00.061749+00	2025-11-12 16:59:00.061751+00
20	auto_create_daily_attendance	2025-11-13 16:00:00.043343+00	2025-11-13 16:00:00.311527+00	0.268	t	Auto-create attendance selesai. Total: 30 karyawan, Created: 20, Skipped: 10, Errors: 0	\N	{"date": "2025-11-13", "total_employees": 30, "created": 20, "skipped": 10, "errors": 0}	2025-11-13 16:00:00.319472+00	2025-11-13 16:00:00.319479+00
21	mark_invalid_no_checkout	2025-11-13 16:59:00.004611+00	2025-11-13 16:59:00.064514+00	0.060	t	Mark invalid no checkout selesai. Total ditemukan: 1, Updated: 1, Errors: 0	\N	{"date": "2025-11-13", "total_found": 1, "updated": 1, "errors": 0}	2025-11-13 16:59:00.065241+00	2025-11-13 16:59:00.065244+00
22	auto_create_daily_attendance	2025-11-14 16:00:00.103976+00	2025-11-14 16:00:00.822762+00	0.719	t	Auto-create attendance selesai. Total: 30 karyawan, Created: 19, Skipped: 11, Errors: 0	\N	{"date": "2025-11-14", "total_employees": 30, "created": 19, "skipped": 11, "errors": 0}	2025-11-14 16:00:00.832066+00	2025-11-14 16:00:00.832071+00
23	mark_invalid_no_checkout	2025-11-14 16:59:00.003928+00	2025-11-14 16:59:00.050215+00	0.046	t	Mark invalid no checkout selesai. Total ditemukan: 4, Updated: 4, Errors: 0	\N	{"date": "2025-11-14", "total_found": 4, "updated": 4, "errors": 0}	2025-11-14 16:59:00.050996+00	2025-11-14 16:59:00.050998+00
24	auto_create_daily_attendance	2025-11-15 16:00:00.157975+00	2025-11-15 16:00:02.730849+00	2.573	t	Auto-create attendance selesai. Total: 30 karyawan, Created: 22, Skipped: 8, Errors: 0	\N	{"date": "2025-11-15", "total_employees": 30, "created": 22, "skipped": 8, "errors": 0}	2025-11-15 16:00:02.744155+00	2025-11-15 16:00:02.744163+00
25	mark_invalid_no_checkout	2025-11-15 16:59:00.006608+00	2025-11-15 16:59:00.03968+00	0.033	t	Mark invalid no checkout selesai. Total ditemukan: 0, Updated: 0, Errors: 0	\N	{"date": "2025-11-15", "total_found": 0, "updated": 0, "errors": 0}	2025-11-15 16:59:00.041033+00	2025-11-15 16:59:00.041037+00
26	auto_create_daily_attendance	2025-11-16 16:00:00.030922+00	2025-11-16 16:00:00.032718+00	0.002	t	Skip auto-create attendance untuk tanggal 2025-11-16 (hari Minggu bukan hari kerja)	\N	{"date": "2025-11-16", "skipped": true, "reason": "Sunday is not a working day"}	2025-11-16 16:00:00.069168+00	2025-11-16 16:00:00.069178+00
27	mark_invalid_no_checkout	2025-11-16 16:59:00.003308+00	2025-11-16 16:59:00.027952+00	0.025	t	Mark invalid no checkout selesai. Total ditemukan: 0, Updated: 0, Errors: 0	\N	{"date": "2025-11-16", "total_found": 0, "updated": 0, "errors": 0}	2025-11-16 16:59:00.029289+00	2025-11-16 16:59:00.029293+00
28	auto_create_daily_attendance	2025-11-17 16:00:00.039128+00	2025-11-17 16:00:00.543175+00	0.504	t	Auto-create attendance selesai. Total: 30 karyawan, Created: 20, Skipped: 10, Errors: 0	\N	{"date": "2025-11-17", "total_employees": 30, "created": 20, "skipped": 10, "errors": 0}	2025-11-17 16:00:00.55028+00	2025-11-17 16:00:00.550286+00
29	mark_invalid_no_checkout	2025-11-17 16:59:00.008784+00	2025-11-17 16:59:00.098673+00	0.090	t	Mark invalid no checkout selesai. Total ditemukan: 2, Updated: 2, Errors: 0	\N	{"date": "2025-11-17", "total_found": 2, "updated": 2, "errors": 0}	2025-11-17 16:59:00.099419+00	2025-11-17 16:59:00.099422+00
31	mark_invalid_no_checkout	2025-11-18 16:59:00.003493+00	2025-11-18 16:59:00.024855+00	0.021	t	Mark invalid no checkout selesai. Total ditemukan: 0, Updated: 0, Errors: 0	\N	{"date": "2025-11-18", "total_found": 0, "updated": 0, "errors": 0}	2025-11-18 16:59:00.025885+00	2025-11-18 16:59:00.025889+00
30	auto_create_daily_attendance	2025-11-18 16:00:00.037326+00	2025-11-18 16:00:00.629393+00	0.592	t	Auto-create attendance selesai. Total: 30 karyawan, Created: 20, Skipped: 10, Errors: 0	\N	{"date": "2025-11-18", "total_employees": 30, "created": 20, "skipped": 10, "errors": 0}	2025-11-18 16:00:00.637822+00	2025-11-18 16:00:00.637826+00
32	auto_create_daily_attendance	2025-11-19 16:00:00.032527+00	2025-11-19 16:00:00.599122+00	0.567	t	Auto-create attendance selesai. Total: 30 karyawan, Created: 20, Skipped: 10, Errors: 0	\N	{"date": "2025-11-19", "total_employees": 30, "created": 20, "skipped": 10, "errors": 0}	2025-11-19 16:00:00.606487+00	2025-11-19 16:00:00.606494+00
34	auto_create_daily_attendance	2025-11-20 16:00:00.029834+00	2025-11-20 16:00:00.269354+00	0.240	t	Auto-create attendance selesai. Total: 30 karyawan, Created: 19, Skipped: 11, Errors: 0	\N	{"date": "2025-11-20", "total_employees": 30, "created": 19, "skipped": 11, "errors": 0}	2025-11-20 16:00:00.275897+00	2025-11-20 16:00:00.275903+00
37	mark_invalid_no_checkout	2025-11-21 16:59:00.002287+00	2025-11-21 16:59:00.034546+00	0.032	t	Mark invalid no checkout selesai. Total ditemukan: 2, Updated: 2, Errors: 0	\N	{"date": "2025-11-21", "total_found": 2, "updated": 2, "errors": 0}	2025-11-21 16:59:00.035289+00	2025-11-21 16:59:00.035292+00
41	mark_invalid_no_checkout	2025-11-23 16:59:00.006634+00	2025-11-23 16:59:00.114612+00	0.108	t	Mark invalid no checkout selesai. Total ditemukan: 0, Updated: 0, Errors: 0	\N	{"date": "2025-11-23", "total_found": 0, "updated": 0, "errors": 0}	2025-11-23 16:59:00.117073+00	2025-11-23 16:59:00.117077+00
43	mark_invalid_no_checkout	2025-11-24 16:59:00.003689+00	2025-11-24 16:59:00.04105+00	0.037	t	Mark invalid no checkout selesai. Total ditemukan: 4, Updated: 4, Errors: 0	\N	{"date": "2025-11-24", "total_found": 4, "updated": 4, "errors": 0}	2025-11-24 16:59:00.041688+00	2025-11-24 16:59:00.04169+00
33	mark_invalid_no_checkout	2025-11-19 16:59:00.002649+00	2025-11-19 16:59:00.03987+00	0.037	t	Mark invalid no checkout selesai. Total ditemukan: 1, Updated: 1, Errors: 0	\N	{"date": "2025-11-19", "total_found": 1, "updated": 1, "errors": 0}	2025-11-19 16:59:00.0407+00	2025-11-19 16:59:00.040704+00
35	mark_invalid_no_checkout	2025-11-20 16:59:00.003109+00	2025-11-20 16:59:00.037205+00	0.034	t	Mark invalid no checkout selesai. Total ditemukan: 2, Updated: 2, Errors: 0	\N	{"date": "2025-11-20", "total_found": 2, "updated": 2, "errors": 0}	2025-11-20 16:59:00.038021+00	2025-11-20 16:59:00.038024+00
38	auto_create_daily_attendance	2025-11-22 16:00:00.20408+00	2025-11-22 16:00:02.916993+00	2.713	t	Auto-create attendance selesai. Total: 30 karyawan, Created: 22, Skipped: 8, Errors: 0	\N	{"date": "2025-11-22", "total_employees": 30, "created": 22, "skipped": 8, "errors": 0}	2025-11-22 16:00:02.929738+00	2025-11-22 16:00:02.929746+00
39	mark_invalid_no_checkout	2025-11-22 16:59:00.004601+00	2025-11-22 16:59:00.041706+00	0.037	t	Mark invalid no checkout selesai. Total ditemukan: 5, Updated: 5, Errors: 0	\N	{"date": "2025-11-22", "total_found": 5, "updated": 5, "errors": 0}	2025-11-22 16:59:00.042319+00	2025-11-22 16:59:00.042321+00
36	auto_create_daily_attendance	2025-11-21 16:00:00.03105+00	2025-11-21 16:00:00.53069+00	0.500	t	Auto-create attendance selesai. Total: 30 karyawan, Created: 19, Skipped: 11, Errors: 0	\N	{"date": "2025-11-21", "total_employees": 30, "created": 19, "skipped": 11, "errors": 0}	2025-11-21 16:00:00.537578+00	2025-11-21 16:00:00.537583+00
40	auto_create_daily_attendance	2025-11-23 16:00:00.081503+00	2025-11-23 16:00:00.085745+00	0.004	t	Skip auto-create attendance untuk tanggal 2025-11-23 (hari Minggu bukan hari kerja)	\N	{"date": "2025-11-23", "skipped": true, "reason": "Sunday is not a working day"}	2025-11-23 16:00:00.259268+00	2025-11-23 16:00:00.259284+00
42	auto_create_daily_attendance	2025-11-24 16:00:00.042129+00	2025-11-24 16:00:00.655187+00	0.613	t	Auto-create attendance selesai. Total: 30 karyawan, Created: 20, Skipped: 10, Errors: 0	\N	{"date": "2025-11-24", "total_employees": 30, "created": 20, "skipped": 10, "errors": 0}	2025-11-24 16:00:00.662841+00	2025-11-24 16:00:00.662846+00
44	auto_create_daily_attendance	2025-11-25 16:00:00.048123+00	2025-11-25 16:00:00.605905+00	0.558	t	Auto-create attendance selesai. Total: 30 karyawan, Created: 21, Skipped: 9, Errors: 0	\N	{"date": "2025-11-25", "total_employees": 30, "created": 21, "skipped": 9, "errors": 0}	2025-11-25 16:00:00.671657+00	2025-11-25 16:00:00.671662+00
45	mark_invalid_no_checkout	2025-11-25 16:59:00.004201+00	2025-11-25 16:59:00.058314+00	0.054	t	Mark invalid no checkout selesai. Total ditemukan: 5, Updated: 5, Errors: 0	\N	{"date": "2025-11-25", "total_found": 5, "updated": 5, "errors": 0}	2025-11-25 16:59:00.059221+00	2025-11-25 16:59:00.059225+00
46	auto_create_daily_attendance	2025-11-26 16:00:00.052358+00	2025-11-26 16:00:00.628491+00	0.576	t	Auto-create attendance selesai. Total: 30 karyawan, Created: 22, Skipped: 8, Errors: 0	\N	{"date": "2025-11-26", "total_employees": 30, "created": 22, "skipped": 8, "errors": 0}	2025-11-26 16:00:00.638333+00	2025-11-26 16:00:00.63834+00
47	mark_invalid_no_checkout	2025-11-26 16:59:00.005305+00	2025-11-26 16:59:00.041835+00	0.037	t	Mark invalid no checkout selesai. Total ditemukan: 2, Updated: 2, Errors: 0	\N	{"date": "2025-11-26", "total_found": 2, "updated": 2, "errors": 0}	2025-11-26 16:59:00.042705+00	2025-11-26 16:59:00.042708+00
48	auto_create_daily_attendance	2025-11-27 16:00:00.144734+00	2025-11-27 16:00:01.5296+00	1.385	t	Auto-create attendance selesai. Total: 30 karyawan, Created: 19, Skipped: 11, Errors: 0	\N	{"date": "2025-11-27", "total_employees": 30, "created": 19, "skipped": 11, "errors": 0}	2025-11-27 16:00:01.551518+00	2025-11-27 16:00:01.551525+00
49	mark_invalid_no_checkout	2025-11-27 16:59:00.005711+00	2025-11-27 16:59:00.154608+00	0.149	t	Mark invalid no checkout selesai. Total ditemukan: 1, Updated: 1, Errors: 0	\N	{"date": "2025-11-27", "total_found": 1, "updated": 1, "errors": 0}	2025-11-27 16:59:00.157602+00	2025-11-27 16:59:00.157606+00
50	auto_create_daily_attendance	2025-11-28 16:00:00.04831+00	2025-11-28 16:00:00.63868+00	0.590	t	Auto-create attendance selesai. Total: 30 karyawan, Created: 21, Skipped: 9, Errors: 0	\N	{"date": "2025-11-28", "total_employees": 30, "created": 21, "skipped": 9, "errors": 0}	2025-11-28 16:00:00.646732+00	2025-11-28 16:00:00.646738+00
51	mark_invalid_no_checkout	2025-11-28 16:59:00.003353+00	2025-11-28 16:59:00.023033+00	0.020	t	Mark invalid no checkout selesai. Total ditemukan: 0, Updated: 0, Errors: 0	\N	{"date": "2025-11-28", "total_found": 0, "updated": 0, "errors": 0}	2025-11-28 16:59:00.024109+00	2025-11-28 16:59:00.024114+00
52	auto_create_daily_attendance	2025-11-29 16:00:00.002223+00	2025-11-29 16:00:00.237344+00	0.235	t	Auto-create attendance selesai. Total: 30 karyawan, Created: 22, Skipped: 8, Errors: 0	\N	{"date": "2025-11-29", "total_employees": 30, "created": 22, "skipped": 8, "errors": 0}	2025-11-29 16:00:00.240267+00	2025-11-29 16:00:00.240271+00
53	mark_invalid_no_checkout	2025-11-29 16:30:00.001615+00	2025-11-29 16:30:00.016737+00	0.015	t	Mark invalid no checkout selesai. Total ditemukan: 2, Updated: 2, Errors: 0	\N	{"date": "2025-11-29", "total_found": 2, "updated": 2, "errors": 0}	2025-11-29 16:30:00.019843+00	2025-11-29 16:30:00.019846+00
54	auto_create_daily_attendance	2025-11-30 16:00:00.040078+00	2025-11-30 16:00:00.251255+00	0.211	t	Auto-create attendance selesai. Total: 30 karyawan, Created: 4, Skipped: 26, Errors: 0	\N	{"date": "2025-11-30", "total_employees": 30, "created": 4, "skipped": 26, "errors": 0}	2025-11-30 16:00:00.277666+00	2025-11-30 16:00:00.277672+00
55	mark_invalid_no_checkout	2025-11-30 16:30:00.003666+00	2025-11-30 16:30:00.0252+00	0.022	t	Mark invalid no checkout selesai. Total ditemukan: 0, Updated: 0, Errors: 0	\N	{"date": "2025-11-30", "total_found": 0, "updated": 0, "errors": 0}	2025-11-30 16:30:00.026082+00	2025-11-30 16:30:00.026086+00
56	auto_create_daily_attendance	2025-12-01 16:00:00.123832+00	2025-12-01 16:00:00.913136+00	0.789	t	Auto-create attendance selesai. Total: 30 karyawan, Created: 21, Skipped: 9, Errors: 0	\N	{"date": "2025-12-01", "total_employees": 30, "created": 21, "skipped": 9, "errors": 0}	2025-12-01 16:00:00.924482+00	2025-12-01 16:00:00.924489+00
57	mark_invalid_no_checkout	2025-12-01 16:30:00.00453+00	2025-12-01 16:30:00.116103+00	0.112	t	Mark invalid no checkout selesai. Total ditemukan: 1, Updated: 1, Errors: 0	\N	{"date": "2025-12-01", "total_found": 1, "updated": 1, "errors": 0}	2025-12-01 16:30:00.116888+00	2025-12-01 16:30:00.116892+00
58	auto_create_daily_attendance	2025-12-02 16:00:00.030511+00	2025-12-02 16:00:00.235194+00	0.205	t	Auto-create attendance selesai. Total: 30 karyawan, Created: 20, Skipped: 10, Errors: 0	\N	{"date": "2025-12-02", "total_employees": 30, "created": 20, "skipped": 10, "errors": 0}	2025-12-02 16:00:00.243255+00	2025-12-02 16:00:00.243259+00
59	mark_invalid_no_checkout	2025-12-02 16:30:00.002537+00	2025-12-02 16:30:00.038956+00	0.036	t	Mark invalid no checkout selesai. Total ditemukan: 1, Updated: 1, Errors: 0	\N	{"date": "2025-12-02", "total_found": 1, "updated": 1, "errors": 0}	2025-12-02 16:30:00.039575+00	2025-12-02 16:30:00.039578+00
60	auto_create_daily_attendance	2025-12-03 16:00:00.08023+00	2025-12-03 16:00:00.624407+00	0.544	t	Auto-create attendance selesai. Total: 30 karyawan, Created: 19, Skipped: 11, Errors: 0	\N	{"date": "2025-12-03", "total_employees": 30, "created": 19, "skipped": 11, "errors": 0}	2025-12-03 16:00:00.63503+00	2025-12-03 16:00:00.635035+00
61	mark_invalid_no_checkout	2025-12-03 16:30:00.003866+00	2025-12-03 16:30:00.068995+00	0.065	t	Mark invalid no checkout selesai. Total ditemukan: 5, Updated: 5, Errors: 0	\N	{"date": "2025-12-03", "total_found": 5, "updated": 5, "errors": 0}	2025-12-03 16:30:00.06998+00	2025-12-03 16:30:00.069984+00
62	auto_create_daily_attendance	2025-12-04 16:00:00.001321+00	2025-12-04 16:00:00.053297+00	0.052	t	Auto-create attendance selesai. Total: 33 karyawan, Created: 0, Skipped: 33, Errors: 0	\N	{"date": "2025-12-04", "total_employees": 33, "created": 0, "skipped": 33, "errors": 0}	2025-12-04 16:00:00.056302+00	2025-12-04 16:00:00.056306+00
63	mark_invalid_no_checkout	2025-12-04 16:30:00.002632+00	2025-12-04 16:30:00.017874+00	0.015	t	Mark invalid no checkout selesai. Total ditemukan: 4, Updated: 4, Errors: 0	\N	{"date": "2025-12-04", "total_found": 4, "updated": 4, "errors": 0}	2025-12-04 16:30:00.018691+00	2025-12-04 16:30:00.018695+00
64	auto_create_daily_attendance	2025-12-05 16:00:00.049656+00	2025-12-05 16:00:00.275915+00	0.226	t	Auto-create attendance selesai. Total: 33 karyawan, Created: 24, Skipped: 9, Errors: 0	\N	{"date": "2025-12-05", "total_employees": 33, "created": 24, "skipped": 9, "errors": 0}	2025-12-05 16:00:00.343568+00	2025-12-05 16:00:00.343574+00
65	mark_invalid_no_checkout	2025-12-05 16:30:00.003752+00	2025-12-05 16:30:00.058147+00	0.054	t	Mark invalid no checkout selesai. Total ditemukan: 4, Updated: 4, Errors: 0	\N	{"date": "2025-12-05", "total_found": 4, "updated": 4, "errors": 0}	2025-12-05 16:30:00.05871+00	2025-12-05 16:30:00.058713+00
66	auto_create_daily_attendance	2025-12-06 16:00:00.038332+00	2025-12-06 16:00:00.461101+00	0.423	t	Auto-create attendance selesai. Total: 33 karyawan, Created: 30, Skipped: 3, Errors: 0	\N	{"date": "2025-12-06", "total_employees": 33, "created": 30, "skipped": 3, "errors": 0}	2025-12-06 16:00:00.471246+00	2025-12-06 16:00:00.471251+00
67	mark_invalid_no_checkout	2025-12-06 16:30:00.004051+00	2025-12-06 16:30:00.035764+00	0.032	t	Mark invalid no checkout selesai. Total ditemukan: 0, Updated: 0, Errors: 0	\N	{"date": "2025-12-06", "total_found": 0, "updated": 0, "errors": 0}	2025-12-06 16:30:00.037006+00	2025-12-06 16:30:00.03701+00
68	auto_create_daily_attendance	2025-12-07 16:00:00.15436+00	2025-12-07 16:00:02.654123+00	2.500	t	Auto-create attendance selesai. Total: 33 karyawan, Created: 19, Skipped: 14, Errors: 0	\N	{"date": "2025-12-07", "total_employees": 33, "created": 19, "skipped": 14, "errors": 0}	2025-12-07 16:00:02.722226+00	2025-12-07 16:00:02.722233+00
69	mark_invalid_no_checkout	2025-12-07 16:30:00.004924+00	2025-12-07 16:30:00.035276+00	0.030	t	Mark invalid no checkout selesai. Total ditemukan: 0, Updated: 0, Errors: 0	\N	{"date": "2025-12-07", "total_found": 0, "updated": 0, "errors": 0}	2025-12-07 16:30:00.03624+00	2025-12-07 16:30:00.036244+00
70	auto_create_daily_attendance	2025-12-08 16:00:00.034249+00	2025-12-08 16:00:00.378839+00	0.345	t	Auto-create attendance selesai. Total: 33 karyawan, Created: 24, Skipped: 9, Errors: 0	\N	{"date": "2025-12-08", "total_employees": 33, "created": 24, "skipped": 9, "errors": 0}	2025-12-08 16:00:00.387923+00	2025-12-08 16:00:00.387927+00
71	mark_invalid_no_checkout	2025-12-08 16:30:00.005428+00	2025-12-08 16:30:00.052699+00	0.047	t	Mark invalid no checkout selesai. Total ditemukan: 2, Updated: 2, Errors: 0	\N	{"date": "2025-12-08", "total_found": 2, "updated": 2, "errors": 0}	2025-12-08 16:30:00.05363+00	2025-12-08 16:30:00.053635+00
72	auto_create_daily_attendance	2025-12-09 16:00:00.001669+00	2025-12-09 16:00:00.163401+00	0.162	t	Auto-create attendance selesai. Total: 33 karyawan, Created: 22, Skipped: 11, Errors: 0	\N	{"date": "2025-12-09", "total_employees": 33, "created": 22, "skipped": 11, "errors": 0}	2025-12-09 16:00:00.166131+00	2025-12-09 16:00:00.166135+00
73	mark_invalid_no_checkout	2025-12-09 16:30:00.002488+00	2025-12-09 16:30:00.015419+00	0.013	t	Mark invalid no checkout selesai. Total ditemukan: 4, Updated: 4, Errors: 0	\N	{"date": "2025-12-09", "total_found": 4, "updated": 4, "errors": 0}	2025-12-09 16:30:00.016068+00	2025-12-09 16:30:00.016071+00
74	auto_create_daily_attendance	2025-12-10 16:00:00.044715+00	2025-12-10 16:00:00.189074+00	0.144	t	Auto-create attendance selesai. Total: 33 karyawan, Created: 7, Skipped: 26, Errors: 0	\N	{"date": "2025-12-10", "total_employees": 33, "created": 7, "skipped": 26, "errors": 0}	2025-12-10 16:00:00.198405+00	2025-12-10 16:00:00.198412+00
75	mark_invalid_no_checkout	2025-12-10 16:30:00.003135+00	2025-12-10 16:30:00.050995+00	0.048	t	Mark invalid no checkout selesai. Total ditemukan: 2, Updated: 2, Errors: 0	\N	{"date": "2025-12-10", "total_found": 2, "updated": 2, "errors": 0}	2025-12-10 16:30:00.051627+00	2025-12-10 16:30:00.05163+00
76	auto_create_daily_attendance	2025-12-11 16:00:00.043756+00	2025-12-11 16:00:00.248013+00	0.204	t	Auto-create attendance selesai. Total: 33 karyawan, Created: 9, Skipped: 24, Errors: 0	\N	{"date": "2025-12-11", "total_employees": 33, "created": 9, "skipped": 24, "errors": 0}	2025-12-11 16:00:00.25628+00	2025-12-11 16:00:00.256285+00
77	mark_invalid_no_checkout	2025-12-11 16:30:00.004323+00	2025-12-11 16:30:00.052928+00	0.049	t	Mark invalid no checkout selesai. Total ditemukan: 4, Updated: 4, Errors: 0	\N	{"date": "2025-12-11", "total_found": 4, "updated": 4, "errors": 0}	2025-12-11 16:30:00.053622+00	2025-12-11 16:30:00.053625+00
78	auto_create_daily_attendance	2025-12-12 16:00:00.038661+00	2025-12-12 16:00:00.220581+00	0.182	t	Auto-create attendance selesai. Total: 33 karyawan, Created: 11, Skipped: 22, Errors: 0	\N	{"date": "2025-12-12", "total_employees": 33, "created": 11, "skipped": 22, "errors": 0}	2025-12-12 16:00:00.228883+00	2025-12-12 16:00:00.228888+00
79	mark_invalid_no_checkout	2025-12-12 16:30:00.00517+00	2025-12-12 16:30:00.072592+00	0.067	t	Mark invalid no checkout selesai. Total ditemukan: 3, Updated: 3, Errors: 0	\N	{"date": "2025-12-12", "total_found": 3, "updated": 3, "errors": 0}	2025-12-12 16:30:00.073502+00	2025-12-12 16:30:00.073505+00
80	auto_create_daily_attendance	2025-12-13 16:00:00.03889+00	2025-12-13 16:00:00.26396+00	0.225	t	Auto-create attendance selesai. Total: 33 karyawan, Created: 11, Skipped: 22, Errors: 0	\N	{"date": "2025-12-13", "total_employees": 33, "created": 11, "skipped": 22, "errors": 0}	2025-12-13 16:00:00.312751+00	2025-12-13 16:00:00.312757+00
81	mark_invalid_no_checkout	2025-12-13 16:30:00.003458+00	2025-12-13 16:30:00.048153+00	0.045	t	Mark invalid no checkout selesai. Total ditemukan: 3, Updated: 3, Errors: 0	\N	{"date": "2025-12-13", "total_found": 3, "updated": 3, "errors": 0}	2025-12-13 16:30:00.048764+00	2025-12-13 16:30:00.048766+00
82	auto_create_daily_attendance	2025-12-14 16:00:00.042899+00	2025-12-14 16:00:00.25468+00	0.212	t	Auto-create attendance selesai. Total: 33 karyawan, Created: 9, Skipped: 24, Errors: 0	\N	{"date": "2025-12-14", "total_employees": 33, "created": 9, "skipped": 24, "errors": 0}	2025-12-14 16:00:00.263151+00	2025-12-14 16:00:00.263154+00
83	mark_invalid_no_checkout	2025-12-14 16:30:00.002905+00	2025-12-14 16:30:00.049238+00	0.046	t	Mark invalid no checkout selesai. Total ditemukan: 0, Updated: 0, Errors: 0	\N	{"date": "2025-12-14", "total_found": 0, "updated": 0, "errors": 0}	2025-12-14 16:30:00.050872+00	2025-12-14 16:30:00.050876+00
84	auto_create_daily_attendance	2025-12-15 16:00:00.159729+00	2025-12-15 16:00:01.528784+00	1.369	t	Auto-create attendance selesai. Total: 33 karyawan, Created: 8, Skipped: 25, Errors: 0	\N	{"date": "2025-12-15", "total_employees": 33, "created": 8, "skipped": 25, "errors": 0}	2025-12-15 16:00:01.561822+00	2025-12-15 16:00:01.561827+00
85	mark_invalid_no_checkout	2025-12-15 16:30:00.005786+00	2025-12-15 16:30:00.074793+00	0.069	t	Mark invalid no checkout selesai. Total ditemukan: 3, Updated: 3, Errors: 0	\N	{"date": "2025-12-15", "total_found": 3, "updated": 3, "errors": 0}	2025-12-15 16:30:00.075507+00	2025-12-15 16:30:00.075509+00
86	auto_create_daily_attendance	2025-12-16 16:00:00.047206+00	2025-12-16 16:00:00.351909+00	0.305	t	Auto-create attendance selesai. Total: 33 karyawan, Created: 8, Skipped: 25, Errors: 0	\N	{"date": "2025-12-16", "total_employees": 33, "created": 8, "skipped": 25, "errors": 0}	2025-12-16 16:00:00.367552+00	2025-12-16 16:00:00.367559+00
87	mark_invalid_no_checkout	2025-12-16 16:30:00.004359+00	2025-12-16 16:30:00.063632+00	0.059	t	Mark invalid no checkout selesai. Total ditemukan: 4, Updated: 4, Errors: 0	\N	{"date": "2025-12-16", "total_found": 4, "updated": 4, "errors": 0}	2025-12-16 16:30:00.064682+00	2025-12-16 16:30:00.064686+00
88	auto_create_daily_attendance	2025-12-17 16:00:00.036893+00	2025-12-17 16:00:00.446617+00	0.410	t	Auto-create attendance selesai. Total: 33 karyawan, Created: 7, Skipped: 26, Errors: 0	\N	{"date": "2025-12-17", "total_employees": 33, "created": 7, "skipped": 26, "errors": 0}	2025-12-17 16:00:00.457061+00	2025-12-17 16:00:00.457068+00
89	mark_invalid_no_checkout	2025-12-17 16:30:00.004386+00	2025-12-17 16:30:00.069972+00	0.066	t	Mark invalid no checkout selesai. Total ditemukan: 1, Updated: 1, Errors: 0	\N	{"date": "2025-12-17", "total_found": 1, "updated": 1, "errors": 0}	2025-12-17 16:30:00.070625+00	2025-12-17 16:30:00.070627+00
\.


--
-- Data for Name: leave_requests; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.leave_requests (id, employee_id, leave_type, start_date, end_date, total_days, reason, created_by, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: permissions; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.permissions (id, code, description, resource, action, created_at, updated_at) FROM stdin;
1	employee.read	View employee data (all employees)	employee	read	2025-11-02 19:01:41.484947+00	2025-11-02 19:01:41.484947+00
2	employee.create	Create new employee	employee	create	2025-11-02 19:01:41.484947+00	2025-11-02 19:01:41.484947+00
3	employee.update	Update employee data	employee	update	2025-11-02 19:01:41.484947+00	2025-11-02 19:01:41.484947+00
4	employee.delete	Delete/deactivate employee	employee	delete	2025-11-02 19:01:41.484947+00	2025-11-02 19:01:41.484947+00
5	employee.export	Export employee data	employee	export	2025-11-02 19:01:41.484947+00	2025-11-02 19:01:41.484947+00
6	org_unit.read	View organization units	org_unit	read	2025-11-02 19:01:41.484947+00	2025-11-02 19:01:41.484947+00
7	org_unit.create	Create organization unit	org_unit	create	2025-11-02 19:01:41.484947+00	2025-11-02 19:01:41.484947+00
8	org_unit.update	Update organization unit	org_unit	update	2025-11-02 19:01:41.484947+00	2025-11-02 19:01:41.484947+00
9	org_unit.delete	Delete organization unit	org_unit	delete	2025-11-02 19:01:41.484947+00	2025-11-02 19:01:41.484947+00
10	leave_request.read_own	View own leave requests	leave_request	read_own	2025-11-02 19:01:41.484947+00	2025-11-02 19:01:41.484947+00
11	leave_request.read	View specific leave request by ID	leave_request	read	2025-11-02 19:01:41.484947+00	2025-11-02 19:01:41.484947+00
12	leave_request.read_all	View all leave requests	leave_request	read_all	2025-11-02 19:01:41.484947+00	2025-11-02 19:01:41.484947+00
13	leave_request.create	Create leave request	leave_request	create	2025-11-02 19:01:41.484947+00	2025-11-02 19:01:41.484947+00
14	leave_request.update	Update leave request	leave_request	update	2025-11-02 19:01:41.484947+00	2025-11-02 19:01:41.484947+00
15	leave_request.delete	Delete leave request	leave_request	delete	2025-11-02 19:01:41.484947+00	2025-11-02 19:01:41.484947+00
16	leave_request.approve	Approve/reject leave request	leave_request	approve	2025-11-02 19:01:41.484947+00	2025-11-02 19:01:41.484947+00
17	attendance.create	Create attendance (check-in/check-out)	attendance	create	2025-11-02 19:01:41.484947+00	2025-11-02 19:01:41.484947+00
18	attendance.read_own	View own attendance history	attendance	read_own	2025-11-02 19:01:41.484947+00	2025-11-02 19:01:41.484947+00
19	attendance.read_team	View team/subordinates attendance	attendance	read_team	2025-11-02 19:01:41.484947+00	2025-11-02 19:01:41.484947+00
20	attendance.read	View specific attendance by ID	attendance	read	2025-11-02 19:01:41.484947+00	2025-11-02 19:01:41.484947+00
21	attendance.read_all	View all attendances with filters	attendance	read_all	2025-11-02 19:01:41.484947+00	2025-11-02 19:01:41.484947+00
22	attendance.update	Update attendance record	attendance	update	2025-11-02 19:01:41.484947+00	2025-11-02 19:01:41.484947+00
23	attendance.approve	Approve attendance corrections	attendance	approve	2025-11-02 19:01:41.484947+00	2025-11-02 19:01:41.484947+00
24	attendance.export	Export attendance data	attendance	export	2025-11-02 19:01:41.484947+00	2025-11-02 19:01:41.484947+00
25	user.read	View user data	user	read	2025-11-02 19:01:41.484947+00	2025-11-02 19:01:41.484947+00
26	user.read_own	View own user profile	user	read_own	2025-11-02 19:01:41.484947+00	2025-11-02 19:01:41.484947+00
27	user.update	Update user data	user	update	2025-11-02 19:01:41.484947+00	2025-11-02 19:01:41.484947+00
28	user.update_own	Update own basic profile	user	update_own	2025-11-02 19:01:41.484947+00	2025-11-02 19:01:41.484947+00
29	user.create	Create new user	user	create	2025-11-02 19:01:41.484947+00	2025-11-02 19:01:41.484947+00
30	user.delete	Delete/deactivate user	user	delete	2025-11-02 19:01:41.484947+00	2025-11-02 19:01:41.484947+00
31	guest.read	View guest accounts	guest	read	2025-11-02 19:01:41.484947+00	2025-11-02 19:01:41.484947+00
32	guest.create	Create guest account	guest	create	2025-11-02 19:01:41.484947+00	2025-11-02 19:01:41.484947+00
33	guest.update	Update guest account	guest	update	2025-11-02 19:01:41.484947+00	2025-11-02 19:01:41.484947+00
34	guest.delete	Delete guest account	guest	delete	2025-11-02 19:01:41.484947+00	2025-11-02 19:01:41.484947+00
35	role.read	View roles	role	read	2025-11-02 19:01:41.484947+00	2025-11-02 19:01:41.484947+00
36	role.create	Create custom roles	role	create	2025-11-02 19:01:41.484947+00	2025-11-02 19:01:41.484947+00
37	role.update	Update roles	role	update	2025-11-02 19:01:41.484947+00	2025-11-02 19:01:41.484947+00
38	role.delete	Delete custom roles	role	delete	2025-11-02 19:01:41.484947+00	2025-11-02 19:01:41.484947+00
39	role.assign	Assign roles to users	role	assign	2025-11-02 19:01:41.484947+00	2025-11-02 19:01:41.484947+00
40	payroll.read	View payroll data	payroll	read	2025-11-02 19:01:41.484947+00	2025-11-02 19:01:41.484947+00
41	payroll.create	Process payroll	payroll	create	2025-11-02 19:01:41.484947+00	2025-11-02 19:01:41.484947+00
42	payroll.update	Update payroll data	payroll	update	2025-11-02 19:01:41.484947+00	2025-11-02 19:01:41.484947+00
43	payroll.approve	Approve payroll	payroll	approve	2025-11-02 19:01:41.484947+00	2025-11-02 19:01:41.484947+00
44	payroll.export	Export payroll data	payroll	export	2025-11-02 19:01:41.484947+00	2025-11-02 19:01:41.484947+00
45	work_submission.read_own	View own work submissions	work_submission	read_own	2025-11-28 14:50:40.90528+00	2025-11-28 14:50:40.90528+00
46	work_submission.read	View specific work submission by ID	work_submission	read	2025-11-28 14:50:40.90528+00	2025-11-28 14:50:40.90528+00
47	work_submission.read_all	View all work submissions	work_submission	read_all	2025-11-28 14:50:40.90528+00	2025-11-28 14:50:40.90528+00
48	work_submission.create	Create work submission	work_submission	create	2025-11-28 14:50:40.90528+00	2025-11-28 14:50:40.90528+00
49	work_submission.update	Update work submission	work_submission	update	2025-11-28 14:50:40.90528+00	2025-11-28 14:50:40.90528+00
50	work_submission.delete	Delete work submission	work_submission	delete	2025-11-28 14:50:40.90528+00	2025-11-28 14:50:40.90528+00
51	work_submission.upload_file	Upload files to work submission	work_submission	upload_file	2025-11-28 14:50:40.90528+00	2025-11-28 14:50:40.90528+00
52	work_submission.delete_file	Delete files from work submission	work_submission	delete_file	2025-11-28 14:50:40.90528+00	2025-11-28 14:50:40.90528+00
61	employee.soft_delete	Archive employee (soft delete)	employee	soft_delete	2025-11-29 15:03:37.035773+00	2025-11-29 15:03:37.035773+00
62	employee.restore	Restore archived employee	employee	restore	2025-11-29 15:03:37.035773+00	2025-11-29 15:03:37.035773+00
63	employee.view_deleted	View archived/deleted employees	employee	view_deleted	2025-11-29 15:03:37.035773+00	2025-11-29 15:03:37.035773+00
64	org_unit.soft_delete	Archive org unit (soft delete)	org_unit	soft_delete	2025-11-29 15:03:37.035773+00	2025-11-29 15:03:37.035773+00
65	org_unit.restore	Restore archived org unit	org_unit	restore	2025-11-29 15:03:37.035773+00	2025-11-29 15:03:37.035773+00
66	org_unit.view_deleted	View archived/deleted org units	org_unit	view_deleted	2025-11-29 15:03:37.035773+00	2025-11-29 15:03:37.035773+00
\.


--
-- Data for Name: role_permissions; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.role_permissions (role_id, permission_id, created_at) FROM stdin;
1	1	2025-11-02 19:01:41.484947+00
1	2	2025-11-02 19:01:41.484947+00
1	3	2025-11-02 19:01:41.484947+00
1	4	2025-11-02 19:01:41.484947+00
1	5	2025-11-02 19:01:41.484947+00
1	6	2025-11-02 19:01:41.484947+00
1	7	2025-11-02 19:01:41.484947+00
1	8	2025-11-02 19:01:41.484947+00
1	9	2025-11-02 19:01:41.484947+00
1	10	2025-11-02 19:01:41.484947+00
1	11	2025-11-02 19:01:41.484947+00
1	12	2025-11-02 19:01:41.484947+00
1	13	2025-11-02 19:01:41.484947+00
1	14	2025-11-02 19:01:41.484947+00
1	15	2025-11-02 19:01:41.484947+00
1	16	2025-11-02 19:01:41.484947+00
1	17	2025-11-02 19:01:41.484947+00
1	18	2025-11-02 19:01:41.484947+00
1	19	2025-11-02 19:01:41.484947+00
1	20	2025-11-02 19:01:41.484947+00
1	21	2025-11-02 19:01:41.484947+00
1	22	2025-11-02 19:01:41.484947+00
1	23	2025-11-02 19:01:41.484947+00
1	24	2025-11-02 19:01:41.484947+00
1	25	2025-11-02 19:01:41.484947+00
1	26	2025-11-02 19:01:41.484947+00
1	27	2025-11-02 19:01:41.484947+00
1	28	2025-11-02 19:01:41.484947+00
1	29	2025-11-02 19:01:41.484947+00
1	30	2025-11-02 19:01:41.484947+00
1	31	2025-11-02 19:01:41.484947+00
1	32	2025-11-02 19:01:41.484947+00
1	33	2025-11-02 19:01:41.484947+00
1	34	2025-11-02 19:01:41.484947+00
1	35	2025-11-02 19:01:41.484947+00
1	36	2025-11-02 19:01:41.484947+00
1	37	2025-11-02 19:01:41.484947+00
1	38	2025-11-02 19:01:41.484947+00
1	39	2025-11-02 19:01:41.484947+00
1	40	2025-11-02 19:01:41.484947+00
1	41	2025-11-02 19:01:41.484947+00
1	42	2025-11-02 19:01:41.484947+00
1	43	2025-11-02 19:01:41.484947+00
1	44	2025-11-02 19:01:41.484947+00
2	1	2025-11-02 19:01:41.484947+00
2	2	2025-11-02 19:01:41.484947+00
2	3	2025-11-02 19:01:41.484947+00
2	5	2025-11-02 19:01:41.484947+00
2	6	2025-11-02 19:01:41.484947+00
2	7	2025-11-02 19:01:41.484947+00
2	8	2025-11-02 19:01:41.484947+00
2	10	2025-11-02 19:01:41.484947+00
2	11	2025-11-02 19:01:41.484947+00
2	12	2025-11-02 19:01:41.484947+00
2	13	2025-11-02 19:01:41.484947+00
2	14	2025-11-02 19:01:41.484947+00
2	16	2025-11-02 19:01:41.484947+00
2	17	2025-11-02 19:01:41.484947+00
2	18	2025-11-02 19:01:41.484947+00
2	19	2025-11-02 19:01:41.484947+00
2	20	2025-11-02 19:01:41.484947+00
2	21	2025-11-02 19:01:41.484947+00
2	22	2025-11-02 19:01:41.484947+00
2	23	2025-11-02 19:01:41.484947+00
2	24	2025-11-02 19:01:41.484947+00
2	25	2025-11-02 19:01:41.484947+00
2	26	2025-11-02 19:01:41.484947+00
2	27	2025-11-02 19:01:41.484947+00
2	28	2025-11-02 19:01:41.484947+00
2	29	2025-11-02 19:01:41.484947+00
2	31	2025-11-02 19:01:41.484947+00
2	32	2025-11-02 19:01:41.484947+00
2	33	2025-11-02 19:01:41.484947+00
2	35	2025-11-02 19:01:41.484947+00
2	40	2025-11-02 19:01:41.484947+00
2	41	2025-11-02 19:01:41.484947+00
2	42	2025-11-02 19:01:41.484947+00
2	43	2025-11-02 19:01:41.484947+00
2	44	2025-11-02 19:01:41.484947+00
3	1	2025-11-02 19:01:41.484947+00
3	6	2025-11-02 19:01:41.484947+00
3	10	2025-11-02 19:01:41.484947+00
3	17	2025-11-02 19:01:41.484947+00
3	18	2025-11-02 19:01:41.484947+00
3	19	2025-11-02 19:01:41.484947+00
3	23	2025-11-02 19:01:41.484947+00
3	26	2025-11-02 19:01:41.484947+00
3	28	2025-11-02 19:01:41.484947+00
4	1	2025-11-02 19:01:41.484947+00
4	6	2025-11-02 19:01:41.484947+00
4	10	2025-11-02 19:01:41.484947+00
4	17	2025-11-02 19:01:41.484947+00
4	18	2025-11-02 19:01:41.484947+00
4	26	2025-11-02 19:01:41.484947+00
4	28	2025-11-02 19:01:41.484947+00
4	40	2025-11-02 19:01:41.484947+00
5	17	2025-11-02 19:01:41.484947+00
5	18	2025-11-02 19:01:41.484947+00
5	26	2025-11-02 19:01:41.484947+00
5	28	2025-11-02 19:01:41.484947+00
1	45	2025-11-28 14:50:40.928015+00
1	46	2025-11-28 14:50:40.928015+00
1	47	2025-11-28 14:50:40.928015+00
1	48	2025-11-28 14:50:40.928015+00
1	49	2025-11-28 14:50:40.928015+00
1	50	2025-11-28 14:50:40.928015+00
1	51	2025-11-28 14:50:40.928015+00
1	52	2025-11-28 14:50:40.928015+00
2	45	2025-11-28 14:50:40.946544+00
2	46	2025-11-28 14:50:40.946544+00
2	47	2025-11-28 14:50:40.946544+00
2	48	2025-11-28 14:50:40.946544+00
2	49	2025-11-28 14:50:40.946544+00
2	51	2025-11-28 14:50:40.946544+00
2	52	2025-11-28 14:50:40.946544+00
3	45	2025-11-28 14:50:40.949328+00
4	45	2025-11-28 14:50:40.949328+00
5	45	2025-11-28 14:50:40.949328+00
3	46	2025-11-28 14:50:40.949328+00
4	46	2025-11-28 14:50:40.949328+00
5	46	2025-11-28 14:50:40.949328+00
3	48	2025-11-28 14:50:40.949328+00
4	48	2025-11-28 14:50:40.949328+00
5	48	2025-11-28 14:50:40.949328+00
3	49	2025-11-28 14:50:40.949328+00
4	49	2025-11-28 14:50:40.949328+00
5	49	2025-11-28 14:50:40.949328+00
3	51	2025-11-28 14:50:40.949328+00
4	51	2025-11-28 14:50:40.949328+00
5	51	2025-11-28 14:50:40.949328+00
3	52	2025-11-28 14:50:40.949328+00
4	52	2025-11-28 14:50:40.949328+00
5	52	2025-11-28 14:50:40.949328+00
1	61	2025-11-29 15:03:37.04091+00
1	62	2025-11-29 15:03:37.04091+00
1	63	2025-11-29 15:03:37.04091+00
1	64	2025-11-29 15:03:37.04091+00
1	65	2025-11-29 15:03:37.04091+00
1	66	2025-11-29 15:03:37.04091+00
2	61	2025-11-29 15:03:37.050093+00
2	64	2025-11-29 15:03:37.050093+00
\.


--
-- Data for Name: roles; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.roles (id, name, description, is_system, created_at, updated_at) FROM stdin;
1	super_admin	Full system access with all permissions	t	2025-11-02 19:01:41.484947+00	2025-11-02 19:01:41.484947+00
2	hr_admin	HR department with employee, org unit, attendance, payroll access	t	2025-11-02 19:01:41.484947+00	2025-11-02 19:01:41.484947+00
3	org_unit_head	Team/unit manager with limited employee and attendance access	t	2025-11-02 19:01:41.484947+00	2025-11-02 19:01:41.484947+00
4	employee	Regular employee with self-service access only	t	2025-11-02 19:01:41.484947+00	2025-11-02 19:01:41.484947+00
5	guest	Temporary users (intern, contractor) with limited access	t	2025-11-02 19:01:41.484947+00	2025-11-02 19:01:41.484947+00
\.


--
-- Data for Name: user_roles; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.user_roles (user_id, role_id, created_at) FROM stdin;
1	1	2025-11-02 19:01:50.215726+00
27	4	2025-11-03 03:56:35.574259+00
27	2	2025-11-03 03:56:40.465549+00
7	4	2025-11-03 04:00:43.637141+00
22	4	2025-11-03 04:00:43.637141+00
21	4	2025-11-03 04:00:43.637141+00
5	4	2025-11-03 04:00:43.637141+00
6	4	2025-11-03 04:00:43.637141+00
20	4	2025-11-03 04:00:43.637141+00
29	4	2025-11-03 05:22:01.752991+00
31	4	2025-11-05 08:57:07.092637+00
32	4	2025-11-05 09:01:55.75931+00
33	4	2025-11-05 09:03:13.370192+00
34	5	2025-11-05 09:09:19.911146+00
35	4	2025-11-05 09:14:21.74542+00
28	4	2025-11-05 09:34:29.041989+00
37	4	2025-12-04 14:38:34.678164+00
38	4	2025-12-04 14:38:34.844176+00
39	4	2025-12-04 14:38:34.993052+00
40	4	2025-12-04 14:38:35.160316+00
40	3	2025-12-04 14:38:35.169752+00
41	4	2025-12-04 14:38:35.32157+00
42	4	2025-12-04 14:38:35.492697+00
43	4	2025-12-04 14:38:35.628183+00
44	4	2025-12-04 14:38:35.768929+00
44	3	2025-12-04 14:38:35.775694+00
45	4	2025-12-04 14:38:35.922248+00
46	4	2025-12-04 14:38:36.142583+00
47	4	2025-12-04 14:38:36.30586+00
48	4	2025-12-04 14:38:36.451377+00
49	4	2025-12-04 14:38:36.661963+00
50	4	2025-12-04 14:38:36.87908+00
51	4	2025-12-04 14:38:37.03866+00
52	4	2025-12-04 14:38:37.242941+00
53	4	2025-12-04 14:38:37.452086+00
54	4	2025-12-04 14:38:37.638083+00
55	4	2025-12-04 14:55:22.592818+00
55	3	2025-12-04 14:55:22.602013+00
56	4	2025-12-04 14:59:51.793913+00
31	1	2025-12-13 03:24:25.128409+00
20	1	2025-12-13 06:00:18.246569+00
\.


--
-- Data for Name: users; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.users (id, sso_id, employee_id, org_unit_id, email, first_name, last_name, account_type, is_active, created_at, updated_at, employee_deleted_at) FROM stdin;
31	40	39	32	richardnarta.arga@gmail.com	Richard	Arya Winarta	regular	t	2025-11-05 08:57:07.002386+00	2025-12-04 14:35:55.899817+00	\N
32	41	41	12	dinidesita.arga@gmail.com	Dini	Desita	regular	t	2025-11-05 09:01:55.718361+00	2025-12-04 14:36:40.603165+00	\N
33	42	42	11	kanayalaras.arga@gmail.com	Kanaya	Laras Sisi	regular	t	2025-11-05 09:03:13.355286+00	2025-12-04 14:37:00.782391+00	\N
37	29	45	21	beninardo.arga@gmail.com	Benny	nardo	regular	t	2025-12-04 14:38:34.665063+00	2025-12-04 14:38:34.665068+00	\N
38	14	46	21	syaifulwahid.arga@gmail.com	Syaiful	Wahid	regular	t	2025-12-04 14:38:34.838204+00	2025-12-04 14:38:34.83821+00	\N
40	15	48	23	fendisusanto.arga@gmail.com	Fendi	Susanto	regular	t	2025-12-04 14:38:35.155289+00	2025-12-04 14:38:35.155293+00	\N
41	32	49	23	zetiara.arga@gmail.com	Zetiara	Maharani	regular	t	2025-12-04 14:38:35.312495+00	2025-12-04 14:38:35.312499+00	\N
42	25	50	23	erikafandi44@gmail.com	Muhammad Eriyana	Apandi	regular	t	2025-12-04 14:38:35.48796+00	2025-12-04 14:38:35.487964+00	\N
43	31	51	23	fazarkurniawan.arga@gmail.com	Rahmad Fazar	Kurniawan	regular	t	2025-12-04 14:38:35.622883+00	2025-12-04 14:38:35.622889+00	\N
44	24	52	24	rudiriyansah92.arga@gmail.com	Rudi	Rianysah	regular	t	2025-12-04 14:38:35.765013+00	2025-12-04 14:38:35.765017+00	\N
45	30	53	25	devisafitriarga@gmail.com	Devi	Sapitri	regular	t	2025-12-04 14:38:35.916117+00	2025-12-04 14:38:35.916121+00	\N
46	45	54	25	rudiekowan.arga01@gmail.com	Rudi	Ekowan	regular	t	2025-12-04 14:38:36.13716+00	2025-12-04 14:38:36.137164+00	\N
48	28	56	27	rahmatimam.arga@gmail.com	Rahmat	Imam	regular	t	2025-12-04 14:38:36.446872+00	2025-12-04 14:38:36.446877+00	\N
49	46	57	27	popyoktareza.arga@gmail.com	Popy	Oktareza	regular	t	2025-12-04 14:38:36.65692+00	2025-12-04 14:38:36.656925+00	\N
51	36	59	29	awangarga031@gmail.com	Awang	Murdiono	regular	t	2025-12-04 14:38:37.033661+00	2025-12-04 14:38:37.033666+00	\N
52	48	60	29	putracenosarga@gmail.com	Wahyu	Saputra	regular	t	2025-12-04 14:38:37.23909+00	2025-12-04 14:38:37.239093+00	\N
53	49	61	29	hengkyargabumiindonesia@gmail.com	Hengky	Rapiansyah	regular	t	2025-12-04 14:38:37.434327+00	2025-12-04 14:38:37.434333+00	\N
54	50	62	30	efendilukman32@gmail.com	Lukman	Efendi	regular	t	2025-12-04 14:38:37.634324+00	2025-12-04 14:38:37.634329+00	\N
39	13	47	22	friansmuhardi.arga@gmail.com	Frians	Muhardi	regular	t	2025-12-04 14:38:34.98824+00	2025-12-04 14:54:07.319044+00	\N
55	26	63	25	sunandararga96@gmail.com	Sunandar	*	regular	t	2025-12-04 14:55:22.588758+00	2025-12-04 14:56:29.668967+00	\N
56	51	64	24	ganangbukhoriargabumi@gmail.com	Ganang	Bukhori	regular	t	2025-12-04 14:59:51.789991+00	2025-12-04 14:59:51.789993+00	\N
50	47	58	27	hendriantopasmaputra.arga@gmail.com	Hendrianto	Pasma Putra	regular	t	2025-12-04 14:38:36.873167+00	2025-12-04 14:38:36.873173+00	\N
47	27	55	27	argadenipernando@gmail.com	Deni	Pernando Hidayat	regular	t	2025-12-04 14:38:36.300846+00	2025-12-15 07:00:47.08309+00	\N
1	11	\N	\N	ahmad.121140173@student.itera.ac.id	Ahmad	Fadillah	regular	t	2025-11-02 19:01:50.21177+00	2025-11-02 19:01:50.211775+00	\N
27	16	20	31	inelayna.arga@gmail.com	Ine	Laynazka	regular	t	2025-07-05 02:31:06.967504+00	2025-12-04 14:31:09.995968+00	\N
6	19	23	33	dieky.arga@gmail.com	Dieky	Laundry	regular	t	2025-07-05 02:33:45.102859+00	2025-12-04 14:31:22.215777+00	\N
7	20	24	31	sintamayangarga@gmail.com	Sinta	Mayang	regular	t	2025-07-05 02:34:21.1047+00	2025-12-04 14:32:02.238993+00	\N
21	22	14	28	haniefan.arga@gmail.com	Muhammad	Haniefan	regular	t	2025-07-05 02:35:41.523081+00	2025-12-04 14:32:46.248564+00	\N
22	23	15	12	hilmanagils.arga@gmail.com	Hilman	Agil	regular	t	2025-07-05 02:36:07.505719+00	2025-12-04 14:34:31.47115+00	\N
5	35	22	33	zamzami.arga@gmail.com	Zam	Zami	regular	t	2025-08-01 02:51:05.498494+00	2025-12-04 14:35:01.209838+00	\N
29	38	\N	\N	ragvindrdiluc85@gmail.com	Ahmad	fadillah	regular	t	2025-11-03 05:22:01.730529+00	2025-11-03 05:22:01.730534+00	\N
28	37	40	\N	mfadlikurniawan.arga@gmail.com	M  Fadli	Kurniawan	regular	t	2025-10-10 08:45:24.503205+00	2025-11-05 09:33:51.950665+00	\N
35	44	44	34	denipambudi.arga@gmail.com	Deni	Pambudi	regular	t	2025-11-05 09:14:21.738416+00	2025-12-04 14:22:46.996663+00	\N
34	43	43	17	ahmad.fadilah0210@gmail.com	Ahmad	Fadilah	guest	t	2025-11-05 09:09:19.850471+00	2025-12-04 14:23:11.558515+00	\N
20	21	13	20	ikhwanferdian.arga@gmail.com	ikhwan	Ferdian	regular	t	2025-07-05 02:35:19.218371+00	2025-12-04 14:30:57.690231+00	\N
\.


--
-- Data for Name: work_submissions; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.work_submissions (id, employee_id, submission_month, title, description, files, status, submitted_at, created_by, created_at, updated_at) FROM stdin;
1	43	2025-11-01	Laporan Kerja November 2025 - Ahmad Fadilah	\N	[{"file_url": null, "file_name": "report november ahmad fadillah.pdf", "file_path": "work_submissions/43/2025/11/1/5dcde32c-96f6-4704-befd-a74a3caf1294.pdf", "file_size": 497093, "file_type": "application/pdf"}]	submitted	2025-11-29 18:53:55.842655+00	34	2025-11-29 18:53:34.862514+00	2025-11-29 18:53:55.84365+00
2	40	2025-11-01	Laporan Kerja November 2025 - M  Fadli Kurniawan	\N	[]	submitted	2025-12-01 10:07:12.489633+00	28	2025-12-01 10:07:12.492247+00	2025-12-01 10:07:12.492251+00
3	43	2025-12-01	Laporan Kerja Desember 2025 - Ahmad Fadilah	\N	[{"file_url": null, "file_name": "IMG-20251204-WA0016.jpg", "file_path": "work_submissions/43/2025/12/3/cd03eab6-36f5-4822-b42e-296e8631b6f2.jpg", "file_size": 142772, "file_type": "image/jpeg"}]	draft	\N	34	2025-12-05 00:36:45.288105+00	2025-12-05 00:36:46.473871+00
\.


--
-- Name: attendances_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.attendances_id_seq', 1174, true);


--
-- Name: guest_accounts_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.guest_accounts_id_seq', 2, true);


--
-- Name: job_executions_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.job_executions_id_seq', 89, true);


--
-- Name: leave_requests_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.leave_requests_id_seq', 1, true);


--
-- Name: permissions_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.permissions_id_seq', 66, true);


--
-- Name: roles_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.roles_id_seq', 5, true);


--
-- Name: users_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.users_id_seq', 56, true);


--
-- Name: work_submissions_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.work_submissions_id_seq', 3, true);


--
-- Name: alembic_version alembic_version_pkc; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.alembic_version
    ADD CONSTRAINT alembic_version_pkc PRIMARY KEY (version_num);


--
-- Name: attendances attendances_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.attendances
    ADD CONSTRAINT attendances_pkey PRIMARY KEY (id);


--
-- Name: guest_accounts guest_accounts_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.guest_accounts
    ADD CONSTRAINT guest_accounts_pkey PRIMARY KEY (id);


--
-- Name: guest_accounts guest_accounts_user_id_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.guest_accounts
    ADD CONSTRAINT guest_accounts_user_id_key UNIQUE (user_id);


--
-- Name: job_executions job_executions_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.job_executions
    ADD CONSTRAINT job_executions_pkey PRIMARY KEY (id);


--
-- Name: leave_requests leave_requests_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.leave_requests
    ADD CONSTRAINT leave_requests_pkey PRIMARY KEY (id);


--
-- Name: permissions permissions_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.permissions
    ADD CONSTRAINT permissions_pkey PRIMARY KEY (id);


--
-- Name: role_permissions role_permissions_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.role_permissions
    ADD CONSTRAINT role_permissions_pkey PRIMARY KEY (role_id, permission_id);


--
-- Name: roles roles_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.roles
    ADD CONSTRAINT roles_pkey PRIMARY KEY (id);


--
-- Name: work_submissions uq_employee_submission_month; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.work_submissions
    ADD CONSTRAINT uq_employee_submission_month UNIQUE (employee_id, submission_month);


--
-- Name: user_roles user_roles_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.user_roles
    ADD CONSTRAINT user_roles_pkey PRIMARY KEY (user_id, role_id);


--
-- Name: users users_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_pkey PRIMARY KEY (id);


--
-- Name: work_submissions work_submissions_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.work_submissions
    ADD CONSTRAINT work_submissions_pkey PRIMARY KEY (id);


--
-- Name: ix_attendances_attendance_date; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_attendances_attendance_date ON public.attendances USING btree (attendance_date);


--
-- Name: ix_attendances_employee_date; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_attendances_employee_date ON public.attendances USING btree (employee_id, attendance_date);


--
-- Name: ix_attendances_employee_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_attendances_employee_id ON public.attendances USING btree (employee_id);


--
-- Name: ix_attendances_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_attendances_id ON public.attendances USING btree (id);


--
-- Name: ix_attendances_org_unit_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_attendances_org_unit_id ON public.attendances USING btree (org_unit_id);


--
-- Name: ix_guest_accounts_user_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_guest_accounts_user_id ON public.guest_accounts USING btree (user_id);


--
-- Name: ix_guest_accounts_valid_until; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_guest_accounts_valid_until ON public.guest_accounts USING btree (valid_until);


--
-- Name: ix_job_executions_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_job_executions_id ON public.job_executions USING btree (id);


--
-- Name: ix_job_executions_job_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_job_executions_job_id ON public.job_executions USING btree (job_id);


--
-- Name: ix_leave_requests_employee_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_leave_requests_employee_id ON public.leave_requests USING btree (employee_id);


--
-- Name: ix_leave_requests_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_leave_requests_id ON public.leave_requests USING btree (id);


--
-- Name: ix_leave_requests_leave_type; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_leave_requests_leave_type ON public.leave_requests USING btree (leave_type);


--
-- Name: ix_permissions_action; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_permissions_action ON public.permissions USING btree (action);


--
-- Name: ix_permissions_code; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX ix_permissions_code ON public.permissions USING btree (code);


--
-- Name: ix_permissions_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_permissions_id ON public.permissions USING btree (id);


--
-- Name: ix_permissions_resource; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_permissions_resource ON public.permissions USING btree (resource);


--
-- Name: ix_roles_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_roles_id ON public.roles USING btree (id);


--
-- Name: ix_roles_name; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX ix_roles_name ON public.roles USING btree (name);


--
-- Name: ix_users_account_type; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_users_account_type ON public.users USING btree (account_type);


--
-- Name: ix_users_email; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX ix_users_email ON public.users USING btree (email);


--
-- Name: ix_users_employee_deleted_at; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_users_employee_deleted_at ON public.users USING btree (employee_deleted_at);


--
-- Name: ix_users_employee_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_users_employee_id ON public.users USING btree (employee_id);


--
-- Name: ix_users_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_users_id ON public.users USING btree (id);


--
-- Name: ix_users_org_unit_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_users_org_unit_id ON public.users USING btree (org_unit_id);


--
-- Name: ix_users_sso_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX ix_users_sso_id ON public.users USING btree (sso_id);


--
-- Name: ix_work_submissions_employee_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_work_submissions_employee_id ON public.work_submissions USING btree (employee_id);


--
-- Name: ix_work_submissions_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_work_submissions_id ON public.work_submissions USING btree (id);


--
-- Name: ix_work_submissions_status; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_work_submissions_status ON public.work_submissions USING btree (status);


--
-- Name: ix_work_submissions_submission_month; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_work_submissions_submission_month ON public.work_submissions USING btree (submission_month);


--
-- Name: guest_accounts guest_accounts_sponsor_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.guest_accounts
    ADD CONSTRAINT guest_accounts_sponsor_id_fkey FOREIGN KEY (sponsor_id) REFERENCES public.users(id) ON DELETE SET NULL;


--
-- Name: guest_accounts guest_accounts_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.guest_accounts
    ADD CONSTRAINT guest_accounts_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE CASCADE;


--
-- Name: role_permissions role_permissions_permission_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.role_permissions
    ADD CONSTRAINT role_permissions_permission_id_fkey FOREIGN KEY (permission_id) REFERENCES public.permissions(id) ON DELETE CASCADE;


--
-- Name: role_permissions role_permissions_role_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.role_permissions
    ADD CONSTRAINT role_permissions_role_id_fkey FOREIGN KEY (role_id) REFERENCES public.roles(id) ON DELETE CASCADE;


--
-- Name: user_roles user_roles_role_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.user_roles
    ADD CONSTRAINT user_roles_role_id_fkey FOREIGN KEY (role_id) REFERENCES public.roles(id) ON DELETE CASCADE;


--
-- Name: user_roles user_roles_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.user_roles
    ADD CONSTRAINT user_roles_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE CASCADE;


--
-- PostgreSQL database dump complete
--

