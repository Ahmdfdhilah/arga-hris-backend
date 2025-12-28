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
-- Name: update_updated_at_column(); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.update_updated_at_column() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$;


ALTER FUNCTION public.update_updated_at_column() OWNER TO postgres;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: schema_migrations; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.schema_migrations (
    version bigint NOT NULL,
    dirty boolean NOT NULL
);


ALTER TABLE public.schema_migrations OWNER TO postgres;

--
-- Name: tblEmployees; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public."tblEmployees" (
    employee_id integer NOT NULL,
    employee_number character varying(50) NOT NULL,
    employee_name character varying(255) NOT NULL,
    employee_email character varying(255),
    employee_phone character varying(50),
    employee_position character varying(255),
    employee_type character varying(20),
    employee_gender character varying(20),
    employee_org_unit_id integer,
    employee_supervisor_id integer,
    employee_metadata jsonb,
    is_active boolean DEFAULT true,
    created_by integer,
    updated_by integer,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    deleted_at timestamp with time zone,
    deleted_by integer,
    CONSTRAINT "tblEmployees_employee_gender_check" CHECK (((employee_gender)::text = ANY ((ARRAY['male'::character varying, 'female'::character varying])::text[]))),
    CONSTRAINT tblemployees_employee_type_check CHECK (((employee_type)::text = ANY ((ARRAY['on_site'::character varying, 'hybrid'::character varying, 'ho'::character varying])::text[])))
);


ALTER TABLE public."tblEmployees" OWNER TO postgres;

--
-- Name: TABLE "tblEmployees"; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON TABLE public."tblEmployees" IS 'Master employee data';


--
-- Name: COLUMN "tblEmployees".employee_type; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public."tblEmployees".employee_type IS 'Employee work type: on_site, hybrid, or ho (head office)';


--
-- Name: COLUMN "tblEmployees".employee_gender; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public."tblEmployees".employee_gender IS 'Employee gender: male or female';


--
-- Name: tblEmployees_employee_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public."tblEmployees_employee_id_seq"
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public."tblEmployees_employee_id_seq" OWNER TO postgres;

--
-- Name: tblEmployees_employee_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public."tblEmployees_employee_id_seq" OWNED BY public."tblEmployees".employee_id;


--
-- Name: tblOrganizationUnits; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public."tblOrganizationUnits" (
    org_unit_id integer NOT NULL,
    org_unit_code character varying(50) NOT NULL,
    org_unit_name character varying(255) NOT NULL,
    org_unit_type character varying(100) NOT NULL,
    org_unit_parent_id integer,
    org_unit_level integer NOT NULL,
    org_unit_path character varying(500) NOT NULL,
    org_unit_head_id integer,
    org_unit_description text,
    org_unit_metadata jsonb,
    is_active boolean DEFAULT true,
    created_by integer,
    updated_by integer,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    deleted_at timestamp with time zone,
    deleted_by integer
);


ALTER TABLE public."tblOrganizationUnits" OWNER TO postgres;

--
-- Name: TABLE "tblOrganizationUnits"; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON TABLE public."tblOrganizationUnits" IS 'Master organization units - hierarchy structure';


--
-- Name: tblOrganizationUnits_org_unit_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public."tblOrganizationUnits_org_unit_id_seq"
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public."tblOrganizationUnits_org_unit_id_seq" OWNER TO postgres;

--
-- Name: tblOrganizationUnits_org_unit_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public."tblOrganizationUnits_org_unit_id_seq" OWNED BY public."tblOrganizationUnits".org_unit_id;


--
-- Name: tblEmployees employee_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public."tblEmployees" ALTER COLUMN employee_id SET DEFAULT nextval('public."tblEmployees_employee_id_seq"'::regclass);


--
-- Name: tblOrganizationUnits org_unit_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public."tblOrganizationUnits" ALTER COLUMN org_unit_id SET DEFAULT nextval('public."tblOrganizationUnits_org_unit_id_seq"'::regclass);


--
-- Data for Name: schema_migrations; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.schema_migrations (version, dirty) FROM stdin;
5	f
\.


--
-- Data for Name: tblEmployees; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public."tblEmployees" (employee_id, employee_number, employee_name, employee_email, employee_phone, employee_position, employee_type, employee_gender, employee_org_unit_id, employee_supervisor_id, employee_metadata, is_active, created_by, updated_by, created_at, updated_at, deleted_at, deleted_by) FROM stdin;
13	ABI0001	ikhwan Ferdian	ikhwanferdian.arga@gmail.com	6282175282776	Direktur Utama	ho	male	20	13	{}	t	5	31	2025-06-30 07:27:38.432894+00	2025-12-04 14:30:57.685226+00	\N	\N
23	FINC-01	Dieky Laundry	dieky.arga@gmail.com	6285366067271	Staff Payable and Treasury 	ho	male	33	13	{}	t	5	31	2025-06-30 07:57:04.878286+00	2025-12-04 14:31:22.209607+00	\N	\N
45	PRO-002	Benny nardo	beninardo.arga@gmail.com	6282278847069	Procurement Spesialist	on_site	male	21	15	{}	t	1	\N	2025-12-04 14:38:34.52023+00	2025-12-04 14:38:34.52023+00	\N	\N
46	PRO-003	Syaiful Wahid	syaifulwahid.arga@gmail.com	6282175400486	QC and Ops Spesialist	on_site	male	21	15	{}	t	1	\N	2025-12-04 14:38:34.692505+00	2025-12-04 14:38:34.692505+00	\N	\N
59	KEB-01	Awang Murdiono	awangarga031@gmail.com	6282282983405	Manger Kebun	on_site	male	29	13	{}	t	1	31	2025-12-04 14:38:36.902089+00	2025-12-04 14:45:58.647192+00	\N	\N
49	TEAMGUDTANGG-02	Zetiara Maharani	zetiara.arga@gmail.com	6281272794056	Staff QC	on_site	female	23	48	{}	t	1	\N	2025-12-04 14:38:35.181966+00	2025-12-04 14:38:35.181966+00	\N	\N
50	TEAMGUDTANGG-03	Muhammad Eriyana Apandi	erikafandi44@gmail.com	6285266607041	Staff AE	on_site	male	23	48	{}	t	1	\N	2025-12-04 14:38:35.357944+00	2025-12-04 14:38:35.357944+00	\N	\N
51	TEAMGUDTANGG-04	Rahmad Fazar Kurniawan	fazarkurniawan.arga@gmail.com	6282184674997	Staff Administrasi Site	on_site	male	23	48	{}	t	1	\N	2025-12-04 14:38:35.503878+00	2025-12-04 14:38:35.503878+00	\N	\N
53	TEAMGUDLAM-01	Devi Sapitri	devisafitriarga@gmail.com	6281366443948	Staff Administrasi Site	on_site	female	25	41	{}	t	1	\N	2025-12-04 14:38:35.783481+00	2025-12-04 14:38:35.783481+00	\N	\N
54	TEAMGUDLAM-03	Rudi Ekowan	rudiekowan.arga01@gmail.com	6282278050416	Staff QC	on_site	male	25	41	{}	t	1	\N	2025-12-04 14:38:35.937513+00	2025-12-04 14:38:35.937513+00	\N	\N
62	SCD-01	Lukman Efendi	efendilukman32@gmail.com	6282269283017	Manager Sustainibility and Community Development	ho	male	30	13	{}	t	1	31	2025-12-04 14:38:37.463425+00	2025-12-04 14:40:45.775953+00	\N	\N
22	FINC-02	Zam Zami	zamzami.arga@gmail.com	628983705560	Staff Accounting and Tax	ho	male	33	13	{}	t	5	31	2025-06-30 07:56:26.033832+00	2025-12-04 14:40:45.779202+00	\N	\N
48	TEAMGUDTANGG-01	Fendi Susanto	fendisusanto.arga@gmail.com	6281366701448	Kepala Gudang Tanggamus	on_site	male	23	47	{}	t	1	31	2025-12-04 14:38:35.008186+00	2025-12-04 14:42:40.072422+00	\N	\N
52	SUBPROLAM-001	Rudi Riansyah	rudiriyansah92.arga@gmail.com	6281240156706	Team Leader Lampung Barat	on_site	male	24	15	{}	t	1	\N	2025-12-04 14:38:35.64348+00	2025-12-04 14:44:31.848393+00	\N	\N
57	TEAMGUDPA-03	Popy Oktareza	popyoktareza.arga@gmail.com	6283137126595	Staff Administrasi	on_site	female	27	56	{}	t	1	31	2025-12-04 14:38:36.463092+00	2025-12-04 14:45:00.389059+00	\N	\N
56	TEAMGUDPA-02	Rahmat Imam	rahmatimam.arga@gmail.com	6289652468125	Staff QC	on_site	male	27	23	{}	t	1	31	2025-12-04 14:38:36.318023+00	2025-12-04 14:45:00.39674+00	\N	\N
14	COM-01	Muhammad Haniefan	haniefan.arga@gmail.com	6281310804780	Manager Commercial	ho	male	28	13	{}	t	5	31	2025-06-30 07:28:34.381605+00	2025-12-04 14:45:42.729725+00	\N	\N
60	KEB-02	Wahyu Saputra	putracenosarga@gmail.com	6285809330067	Staff Kebun Tanggamus	on_site	male	29	59	{}	t	1	31	2025-12-04 14:38:37.0547+00	2025-12-04 14:45:58.643674+00	\N	\N
61	KEB-03	Hengky Rapiansyah	hengkyargabumiindonesia@gmail.com	6285758477134	Staff Kebun Liwa	on_site	male	29	59	{}	t	1	31	2025-12-04 14:38:37.254004+00	2025-12-04 14:45:58.643674+00	\N	\N
24	HCGA-02	Sinta Mayang	sintamayangarga@gmail.com	6285766893441	Staff General Affairs	ho	female	31	13	{}	t	5	31	2025-06-30 07:57:41.369387+00	2025-12-04 14:45:58.650662+00	\N	\N
47	SUBPROTANGG-001	Frians Muhardi	friansmuhardi.arga@gmail.com	6282182671208	Team Lead Tanggamus	on_site	male	22	15	{}	t	1	31	2025-12-04 14:38:34.857558+00	2025-12-04 14:54:07.313172+00	\N	\N
58	TEAMGUDPA-04	Hendrianto Pasma Putra	hendriantopasmaputra.arga@gmail.com	6285379545585	Staff Senior AE	on_site	male	27	56	{}	t	1	31	2025-12-04 14:38:36.67519+00	2025-12-11 06:34:29.195987+00	\N	\N
55	TEAMGUDPA-01	Deni Pernando Hidayat	argadenipernando@gmail.com	6289612856683	Staff Operasional Pagar Alam	on_site	male	27	56	{}	t	1	31	2025-12-04 14:38:36.154979+00	2025-12-15 07:00:58.37869+00	\N	\N
20	HCGA-01	Ine Laynazka	inelayna.arga@gmail.com	6289523081098	SPV HCGA	ho	female	31	13	{}	t	5	31	2025-06-30 07:53:29.061991+00	2025-12-04 14:31:09.990471+00	\N	\N
42	COM-02	Kanaya Laras Sisi	kanayalaras.arga@gmail.com	6289657119303	Commercial Spesialist	ho	female	28	13	{}	t	27	31	2025-11-05 09:03:13.181876+00	2025-12-04 14:51:10.061931+00	\N	\N
40	COM-03	M. Fadli Kurniawan	mfadlikurniawan.arga@gmail.com		Creatif Staff 	ho	male	28	23	{}	t	27	31	2025-11-05 08:59:04.012831+00	2025-12-04 14:51:43.625551+00	\N	\N
41	PRO-004	Dini Desita	dinidesita.arga@gmail.com	628987681089	Procurement Support	ho	female	21	56	{}	t	27	31	2025-11-05 09:01:55.563838+00	2025-12-04 14:52:26.781835+00	\N	\N
15	PRO-001	Hilman Agil	hilmanagils.arga@gmail.com	6281283859897	Manager Procurement	ho	male	21	23	{}	t	5	31	2025-06-30 07:29:14.904776+00	2025-12-04 14:52:40.900154+00	\N	\N
64	TEAMGUDLAM-04	Ganang Bukhori	ganangbukhoriargabumi@gmail.com	6281367437868	Staff AE 	on_site	male	24	52	{}	t	1	\N	2025-12-04 14:59:51.613111+00	2025-12-04 14:59:51.613111+00	\N	\N
63	TEAMGUDLAM-02	Sunandar	sunandararga96@gmail.com	6285761945552	Staff AE	on_site	male	25	52	{}	t	31	31	2025-12-04 14:55:22.468816+00	2025-12-04 15:03:22.766006+00	\N	\N
39	IT-001	Richard Arya Winarta	richardnarta.arga@gmail.com	6285768207890	Product Development Spesialist	hybrid	male	32	39	{}	t	27	31	2025-11-05 08:57:06.176364+00	2025-12-09 13:14:34.24099+00	\N	\N
43	IT-002	Ahmad Fadilah	ahmad.fadilah0210@gmail.com	6285768207890	Product Development Spesialist	hybrid	male	32	15	{}	t	27	31	2025-11-05 09:09:19.315421+00	2025-12-09 13:14:41.457116+00	\N	\N
44	STRATEGIC-01	Deni Pambudi	denipambudi.arga@gmail.com	6282279013034	Staff BSC 	ho	male	34	\N	{}	t	27	1	2025-11-05 09:14:21.602047+00	2025-12-04 14:22:46.991587+00	\N	\N
\.


--
-- Data for Name: tblOrganizationUnits; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public."tblOrganizationUnits" (org_unit_id, org_unit_code, org_unit_name, org_unit_type, org_unit_parent_id, org_unit_level, org_unit_path, org_unit_head_id, org_unit_description, org_unit_metadata, is_active, created_by, updated_by, created_at, updated_at, deleted_at, deleted_by) FROM stdin;
26	SUB-PROCUREMENT-PAGARALAM	Sub Procurement Pagar Alam	Sub Department	21	3	20.21.26	\N		{}	t	1	31	2025-12-04 14:17:33.378121+00	2025-12-04 14:48:41.337841+00	\N	\N
25	TEAM-GUDANG-LAMPUNG-BARAT	Tim Staff Gudang Lampung Barat	Staff Gudang	24	4	20.21.24.25	\N		{}	t	1	31	2025-12-04 14:17:33.368711+00	2025-12-04 15:00:48.486072+00	\N	\N
30	DEPT-SUSTAINABILITY	Departemen Sustainability & Community Development	Department	20	2	20.30	62		{}	t	1	1	2025-12-04 14:17:33.405129+00	2025-12-04 23:16:04.886392+00	\N	\N
27	TEAM-GUDANG-PAGARALAM	Tim Staff Gudang Pagar Alam	Staff Gudang	26	4	20.21.26.27	56		{}	t	1	1	2025-12-04 14:17:33.385521+00	2025-12-04 23:17:55.779061+00	\N	\N
32	DEPT-RDIT	Departemen R&D dan IT	Department	20	2	20.32	39	Departemen Research & Development dan Information Technology	{}	t	1	1	2025-12-04 14:17:33.418885+00	2025-12-04 23:18:49.598822+00	\N	\N
20	DIRUT	Direktorat	Direktorat	\N	1	20	13	Direktur Utama	{}	t	1	31	2025-12-04 14:17:33.32304+00	2025-12-04 14:23:52.749984+00	\N	\N
31	DEPT-HCGA	Departemen Human Capital & General Affairs	Department	20	2	20.31	20		{}	t	1	31	2025-12-04 14:17:33.411838+00	2025-12-04 14:26:11.214253+00	\N	\N
21	DEPT-PROCUREMENT	Departemen Procurement	Department	20	2	20.21	15		{}	t	1	31	2025-12-04 14:17:33.338403+00	2025-12-04 14:36:38.594984+00	\N	\N
23	TEAM-GUDANG-TANGGAMUS	Tim Staff Gudang Tanggamus	Staff Gudang	22	4	20.21.22.23	48	\N	{}	t	1	1	2025-12-04 14:17:33.353946+00	2025-12-04 14:38:35.011432+00	\N	\N
24	SUB-PROCUREMENT-LAMBAR	Sub Procurement Lampung Barat	Sub Department	21	3	20.21.24	52	\N	{}	t	1	1	2025-12-04 14:17:33.36201+00	2025-12-04 14:38:35.645385+00	\N	\N
34	DEPT-STRATEGIC	Departemen Strategic	Department	20	2	20.34	\N	\N	{}	t	1	1	2025-12-04 14:17:33.432366+00	2025-12-04 14:39:58.52482+00	\N	\N
33	DEPT-FINANCE	Departemen Finance	Department	20	2	20.33	\N		{}	t	1	31	2025-12-04 14:17:33.425816+00	2025-12-04 14:41:21.023024+00	\N	\N
22	SUB-PROCUREMENT-TANGGAMUS	Sub Procurement Tanggamus	Sub Department	21	3	20.21.22	47		{}	t	1	31	2025-12-04 14:17:33.34722+00	2025-12-04 14:42:40.067924+00	\N	\N
28	DEPT-COMMERCIAL	Departemen Commercial	Department	20	2	20.28	14		{}	t	1	31	2025-12-04 14:17:33.392267+00	2025-12-04 14:45:42.726675+00	\N	\N
29	DEPT-PLANTATION	Departemen Plantation	Department	20	2	20.29	59		{}	t	1	31	2025-12-04 14:17:33.39901+00	2025-12-04 14:45:58.640931+00	\N	\N
\.


--
-- Name: tblEmployees_employee_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public."tblEmployees_employee_id_seq"', 64, true);


--
-- Name: tblOrganizationUnits_org_unit_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public."tblOrganizationUnits_org_unit_id_seq"', 34, true);


--
-- Name: schema_migrations schema_migrations_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.schema_migrations
    ADD CONSTRAINT schema_migrations_pkey PRIMARY KEY (version);


--
-- Name: tblEmployees tblEmployees_employee_email_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public."tblEmployees"
    ADD CONSTRAINT "tblEmployees_employee_email_key" UNIQUE (employee_email);


--
-- Name: tblEmployees tblEmployees_employee_number_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public."tblEmployees"
    ADD CONSTRAINT "tblEmployees_employee_number_key" UNIQUE (employee_number);


--
-- Name: tblEmployees tblEmployees_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public."tblEmployees"
    ADD CONSTRAINT "tblEmployees_pkey" PRIMARY KEY (employee_id);


--
-- Name: tblOrganizationUnits tblOrganizationUnits_org_unit_code_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public."tblOrganizationUnits"
    ADD CONSTRAINT "tblOrganizationUnits_org_unit_code_key" UNIQUE (org_unit_code);


--
-- Name: tblOrganizationUnits tblOrganizationUnits_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public."tblOrganizationUnits"
    ADD CONSTRAINT "tblOrganizationUnits_pkey" PRIMARY KEY (org_unit_id);


--
-- Name: idx_employees_deleted_at; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_employees_deleted_at ON public."tblEmployees" USING btree (deleted_at);


--
-- Name: idx_employees_email; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_employees_email ON public."tblEmployees" USING btree (employee_email);


--
-- Name: idx_employees_employee_number; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_employees_employee_number ON public."tblEmployees" USING btree (employee_number);


--
-- Name: idx_employees_gender; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_employees_gender ON public."tblEmployees" USING btree (employee_gender);


--
-- Name: idx_employees_is_active; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_employees_is_active ON public."tblEmployees" USING btree (is_active);


--
-- Name: idx_employees_org_unit_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_employees_org_unit_id ON public."tblEmployees" USING btree (employee_org_unit_id);


--
-- Name: idx_employees_supervisor_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_employees_supervisor_id ON public."tblEmployees" USING btree (employee_supervisor_id);


--
-- Name: idx_employees_type; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_employees_type ON public."tblEmployees" USING btree (employee_type);


--
-- Name: idx_org_units_code; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_org_units_code ON public."tblOrganizationUnits" USING btree (org_unit_code);


--
-- Name: idx_org_units_deleted_at; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_org_units_deleted_at ON public."tblOrganizationUnits" USING btree (deleted_at);


--
-- Name: idx_org_units_head_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_org_units_head_id ON public."tblOrganizationUnits" USING btree (org_unit_head_id);


--
-- Name: idx_org_units_is_active; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_org_units_is_active ON public."tblOrganizationUnits" USING btree (is_active);


--
-- Name: idx_org_units_parent_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_org_units_parent_id ON public."tblOrganizationUnits" USING btree (org_unit_parent_id);


--
-- Name: idx_org_units_path; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_org_units_path ON public."tblOrganizationUnits" USING btree (org_unit_path);


--
-- Name: idx_org_units_type; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_org_units_type ON public."tblOrganizationUnits" USING btree (org_unit_type);


--
-- Name: tblEmployees update_employees_updated_at; Type: TRIGGER; Schema: public; Owner: postgres
--

CREATE TRIGGER update_employees_updated_at BEFORE UPDATE ON public."tblEmployees" FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();


--
-- Name: tblOrganizationUnits update_org_units_updated_at; Type: TRIGGER; Schema: public; Owner: postgres
--

CREATE TRIGGER update_org_units_updated_at BEFORE UPDATE ON public."tblOrganizationUnits" FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();


--
-- Name: tblOrganizationUnits fk_org_unit_head; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public."tblOrganizationUnits"
    ADD CONSTRAINT fk_org_unit_head FOREIGN KEY (org_unit_head_id) REFERENCES public."tblEmployees"(employee_id) ON DELETE SET NULL;


--
-- Name: tblEmployees tblEmployees_employee_org_unit_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public."tblEmployees"
    ADD CONSTRAINT "tblEmployees_employee_org_unit_id_fkey" FOREIGN KEY (employee_org_unit_id) REFERENCES public."tblOrganizationUnits"(org_unit_id) ON DELETE SET NULL;


--
-- Name: tblEmployees tblEmployees_employee_supervisor_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public."tblEmployees"
    ADD CONSTRAINT "tblEmployees_employee_supervisor_id_fkey" FOREIGN KEY (employee_supervisor_id) REFERENCES public."tblEmployees"(employee_id) ON DELETE SET NULL;


--
-- Name: tblOrganizationUnits tblOrganizationUnits_org_unit_parent_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public."tblOrganizationUnits"
    ADD CONSTRAINT "tblOrganizationUnits_org_unit_parent_id_fkey" FOREIGN KEY (org_unit_parent_id) REFERENCES public."tblOrganizationUnits"(org_unit_id) ON DELETE SET NULL;


--
-- PostgreSQL database dump complete
--

