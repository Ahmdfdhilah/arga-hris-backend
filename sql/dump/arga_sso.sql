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
-- Name: applications; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.applications (
    id integer NOT NULL,
    name character varying NOT NULL,
    code character varying NOT NULL,
    description character varying,
    base_url character varying NOT NULL,
    created_at timestamp with time zone,
    updated_at timestamp with time zone
);


ALTER TABLE public.applications OWNER TO postgres;

--
-- Name: applications_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.applications_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.applications_id_seq OWNER TO postgres;

--
-- Name: applications_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.applications_id_seq OWNED BY public.applications.id;


--
-- Name: guest_accounts; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.guest_accounts (
    id integer NOT NULL,
    user_id integer NOT NULL,
    guest_type character varying(50) NOT NULL,
    password_hash character varying(255) NOT NULL,
    valid_from timestamp with time zone NOT NULL,
    valid_until timestamp with time zone NOT NULL,
    sponsor_id integer,
    notes text,
    created_at timestamp with time zone NOT NULL,
    updated_at timestamp with time zone NOT NULL
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
-- Name: user_applications; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.user_applications (
    user_id integer NOT NULL,
    application_id integer NOT NULL
);


ALTER TABLE public.user_applications OWNER TO postgres;

--
-- Name: users; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.users (
    id integer NOT NULL,
    email character varying NOT NULL,
    first_name character varying NOT NULL,
    last_name character varying,
    google_id character varying,
    is_active boolean NOT NULL,
    is_superuser boolean NOT NULL,
    created_at timestamp with time zone,
    updated_at timestamp with time zone,
    account_type character varying(20) DEFAULT 'regular'::character varying NOT NULL
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
-- Name: applications id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.applications ALTER COLUMN id SET DEFAULT nextval('public.applications_id_seq'::regclass);


--
-- Name: guest_accounts id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.guest_accounts ALTER COLUMN id SET DEFAULT nextval('public.guest_accounts_id_seq'::regclass);


--
-- Name: users id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.users ALTER COLUMN id SET DEFAULT nextval('public.users_id_seq'::regclass);


--
-- Data for Name: alembic_version; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.alembic_version (version_num) FROM stdin;
fad7a7084d25
\.


--
-- Data for Name: applications; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.applications (id, name, code, description, base_url, created_at, updated_at) FROM stdin;
2	Company Profile	CP		https://argabumi.id/admin	2025-05-29 15:45:43.205844+00	2025-05-29 15:47:55.153247+00
1	Performance Management	pm	Performance Management System.	https://pm.argabumi.id	2025-05-05 09:48:06.888405+00	2025-08-28 02:24:07.178813+00
3	HRIS Argabumi	HRARGA	\N	https://hris.argabumi.id	2025-11-02 18:37:07.653023+00	2025-11-02 18:37:07.653031+00
4	Arga Executive	ARGA002	Dashboard Monitoring Transaksi	https://analytics.argabumi.id	2025-11-12 07:06:50.584129+00	2025-12-16 17:09:20.611239+00
\.


--
-- Data for Name: guest_accounts; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.guest_accounts (id, user_id, guest_type, password_hash, valid_from, valid_until, sponsor_id, notes, created_at, updated_at) FROM stdin;
2	43	intern	$2b$12$NEF13hVtpfaNAvmrhTWxVu1ct.E9iOBTRayZ.lGLM.IK5rmWxeP4G	2025-11-03 17:00:00+00	2026-05-03 17:00:00+00	\N	Kontrak 	2025-11-05 09:09:19.749367+00	2025-12-04 14:23:11.614314+00
\.


--
-- Data for Name: user_applications; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.user_applications (user_id, application_id) FROM stdin;
5	1
2	1
8	1
9	1
10	1
11	1
11	2
2	2
16	1
17	1
19	1
20	1
21	1
22	1
23	1
33	1
34	1
35	1
38	2
16	3
2	3
8	3
9	3
10	3
13	3
14	3
15	3
17	3
24	3
25	3
26	3
27	3
28	3
29	3
30	3
31	3
32	3
33	3
34	3
5	3
35	3
21	3
22	3
23	3
19	3
20	3
36	3
38	3
37	3
11	3
40	3
41	3
42	3
43	3
44	3
11	4
40	4
5	4
21	4
23	4
41	4
45	3
46	3
47	3
48	3
49	3
50	3
51	3
\.


--
-- Data for Name: users; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.users (id, email, first_name, last_name, google_id, is_active, is_superuser, created_at, updated_at, account_type) FROM stdin;
28	rahmatimam.arga@gmail.com	Rahmat	Imam	108092317252134897107	t	f	2025-07-05 02:39:25.028431+00	2025-12-10 07:14:05.922997+00	regular
30	devisafitriarga@gmail.com	Defi	Sapitri	113619297715603353458	t	f	2025-07-05 02:40:38.886311+00	2025-12-10 07:14:11.02858+00	regular
15	fendisusanto.arga@gmail.com	Fendi	Susanto	115602430059175571057	t	f	2025-07-05 02:30:28.685006+00	2025-12-10 07:14:19.879896+00	regular
32	zetiara.arga@gmail.com	Zetiara	Maharani	106881731592035050655	t	f	2025-07-05 02:41:41.720848+00	2025-12-10 07:14:31.684098+00	regular
29	beninardo.arga@gmail.com	Beni	Nardo	104550046776155371886	t	f	2025-07-05 02:39:51.445312+00	2025-12-10 07:18:23.449656+00	regular
24	rudiriyansah92.arga@gmail.com	Rudi	Riansyah	116653179495596868310	t	f	2025-07-05 02:36:35.782898+00	2025-12-10 07:19:12.509721+00	regular
31	fazarkurniawan.arga@gmail.com	Rahmad	Fazar Kurniawan	105869457836844429226	t	f	2025-07-05 02:41:17.934271+00	2025-12-10 07:19:18.392213+00	regular
46	popyoktareza.arga@gmail.com	Popy	Oktareza	107825590535810058957	t	f	2025-12-04 14:38:36.571743+00	2025-12-10 07:19:36.434079+00	regular
49	hengkyargabumiindonesia@gmail.com	Hengky	Rapiansyah	115794161861146195697	t	f	2025-12-04 14:38:37.347849+00	2025-12-10 07:20:41.692607+00	regular
25	erikafandi44@gmail.com	Muhammad	Eriyana Apandi	115589384602338122727	t	f	2025-07-05 02:37:11.693345+00	2025-12-10 07:24:04.054289+00	regular
51	ganangbukhoriargabumi@gmail.com	Ganang	Bukhori	106551410995734694213	t	f	2025-12-04 14:59:51.722561+00	2025-12-10 07:26:38.556874+00	regular
17	robihanseptian17.arga@gmail.com	Robihan	Septian	\N	t	f	2025-07-05 02:31:43.684708+00	2025-12-04 13:40:57.215529+00	regular
14	syaifulwahid.arga@gmail.com	Syaiful	Wahid	\N	t	f	2025-07-05 02:29:52.987035+00	2025-12-04 13:41:08.578338+00	regular
26	sunandararga96@gmail.com	Sunandar	*	108072576193322955966	t	f	2025-07-05 02:37:39.756708+00	2025-12-10 07:29:11.75506+00	regular
5	paskaljordan@gmail.com	Paskal	Jordan	103577766032917907948	t	t	2025-05-05 16:08:44.583406+00	2025-12-04 13:44:44.689948+00	regular
42	kanayalaras.arga@gmail.com	Kanaya	Laras Sisi	108504108304977046520	t	f	2025-11-05 09:03:13.245352+00	2025-11-06 01:53:08.928404+00	regular
41	dinidesita.arga@gmail.com	Dini	Desita	106897309533878033696	t	f	2025-11-05 09:01:55.617657+00	2025-11-06 02:55:33.675579+00	regular
35	zamzami.arga@gmail.com	Zam	Zami	116315691764119266743	t	f	2025-08-01 02:51:05.498494+00	2025-11-07 03:11:45.93925+00	regular
44	denipambudi.arga@gmail.com	Deni	Pambudi	111039302831922541352	t	f	2025-11-05 09:14:21.653687+00	2025-12-04 13:34:12.423518+00	regular
34	putracenos@gmail.com	Wahyu	Saputra	\N	t	f	2025-07-05 02:42:29.243527+00	2025-12-04 13:39:42.407775+00	regular
33	nisa.arga@gmail.com	Annisa	P Azzahra	\N	t	f	2025-07-05 02:42:05.39904+00	2025-12-04 13:39:47.209882+00	regular
48	putracenosarga@gmail.com	Wahyu	Saputra	101743676291058386643	t	f	2025-12-04 14:38:37.15699+00	2025-12-10 12:15:56.413882+00	regular
47	hendriantopasmaputra.arga@gmail.com	Hendrianto	Pasma Putra	102943100301513049715	t	f	2025-12-04 14:38:36.784343+00	2025-12-11 10:03:09.606062+00	regular
50	efendilukman32@gmail.com	Lukman	Efendi	103307422326204901605	t	f	2025-12-04 14:38:37.561632+00	2025-12-12 03:13:11.722885+00	regular
45	rudiekowan.arga01@gmail.com	Rudi	Ekowan	117822839597304170379	t	f	2025-12-04 14:38:36.04941+00	2025-12-12 08:01:29.278604+00	regular
13	friansmuhardi.arga@gmail.com	Frians	Muhardi	102884458518738291961	t	f	2025-07-05 02:29:15.446502+00	2025-12-15 04:51:00.572675+00	regular
2	muhammad.algifari@if.itera.ac.id	Pak	Habib	110918785119965076411	t	t	2025-05-05 09:08:13.03362+00	2025-05-05 09:47:31.767714+00	regular
43	ahmad.fadilah0210@gmail.com	Ahmad	Fadilah	108025138786015788024	t	f	2025-11-05 09:09:19.390018+00	2025-11-05 09:23:13.621778+00	guest
8	argampm1@gmail.com	Akun PM 1	MPM 1	115894654904472699385	t	f	2025-05-16 01:18:25.846678+00	2025-05-16 01:35:11.066746+00	regular
27	argadenipernando@gmail.com	Deni	Pernando Hidayat	106551439517586250349	t	f	2025-07-05 02:38:59.592778+00	2025-12-15 07:04:52.593422+00	regular
9	argampm2@gmail.com	Akun PM 2	MPM 2	112246419927382175120	t	f	2025-05-16 01:18:58.259052+00	2025-05-16 01:40:54.363209+00	regular
10	argampm3@gmail.com	Akun PM 3	MPM 3	112698199995048924110	t	f	2025-05-16 01:19:35.194899+00	2025-05-16 01:52:46.245287+00	regular
21	ikhwanferdian.arga@gmail.com	ikhwan	Ferdian	115814605363281314991	t	f	2025-07-05 02:35:19.218371+00	2025-09-18 03:49:46.235887+00	regular
22	haniefan.arga@gmail.com	Muhammad	Haniefan	112435635907241430992	t	f	2025-07-05 02:35:41.523081+00	2025-09-18 04:08:59.126324+00	regular
23	hilmanagils.arga@gmail.com	Hilman	Agil	107391348800375529890	t	f	2025-07-05 02:36:07.505719+00	2025-09-18 04:09:01.498271+00	regular
20	sintamayangarga@gmail.com	Sinta	Mayang	111951050857271530090	t	f	2025-07-05 02:34:21.1047+00	2025-09-18 04:16:47.424614+00	regular
38	ragvindrdiluc85@gmail.com	Ahmad	fadillah	109943158860152757740	t	f	2025-10-10 08:49:53.158261+00	2025-10-10 08:49:56.490326+00	regular
37	mfadlikurniawan.arga@gmail.com	M  Fadli	Kurniawan	100798671028868294962	t	f	2025-10-10 08:45:24.503205+00	2025-10-11 03:45:20.012376+00	regular
11	ahmad.121140173@student.itera.ac.id	 Ahmat Itera	Fadillah	104073833676937977982	t	t	2025-05-19 03:04:51.301018+00	2025-11-02 18:37:48.672604+00	regular
16	inelayna.arga@gmail.com	Ine	Laynazka	116203338530598041792	t	t	2025-07-05 02:31:06.967504+00	2025-11-03 05:53:41.446801+00	regular
40	richardnarta.arga@gmail.com	Richard	Arya Winarta	100389420365494483512	t	f	2025-11-05 08:57:06.512716+00	2025-11-05 08:57:55.167276+00	regular
36	awangarga031@gmail.com	Awang	Murdiono	116515787052887229045	t	f	2025-09-18 07:14:59.272146+00	2025-12-04 13:39:37.004724+00	regular
19	dieky.arga@gmail.com	Dieky	Laundry	109246877509651158113	t	f	2025-07-05 02:33:45.102859+00	2025-12-04 14:22:42.958905+00	regular
\.


--
-- Name: applications_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.applications_id_seq', 4, true);


--
-- Name: guest_accounts_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.guest_accounts_id_seq', 2, true);


--
-- Name: users_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.users_id_seq', 51, true);


--
-- Name: alembic_version alembic_version_pkc; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.alembic_version
    ADD CONSTRAINT alembic_version_pkc PRIMARY KEY (version_num);


--
-- Name: applications applications_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.applications
    ADD CONSTRAINT applications_pkey PRIMARY KEY (id);


--
-- Name: guest_accounts guest_accounts_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.guest_accounts
    ADD CONSTRAINT guest_accounts_pkey PRIMARY KEY (id);


--
-- Name: user_applications user_applications_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.user_applications
    ADD CONSTRAINT user_applications_pkey PRIMARY KEY (user_id, application_id);


--
-- Name: users users_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_pkey PRIMARY KEY (id);


--
-- Name: ix_applications_code; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX ix_applications_code ON public.applications USING btree (code);


--
-- Name: ix_applications_name; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX ix_applications_name ON public.applications USING btree (name);


--
-- Name: ix_guest_accounts_user_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX ix_guest_accounts_user_id ON public.guest_accounts USING btree (user_id);


--
-- Name: ix_guest_accounts_valid_until; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_guest_accounts_valid_until ON public.guest_accounts USING btree (valid_until);


--
-- Name: ix_users_account_type; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_users_account_type ON public.users USING btree (account_type);


--
-- Name: ix_users_email; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX ix_users_email ON public.users USING btree (email);


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
-- Name: user_applications user_applications_application_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.user_applications
    ADD CONSTRAINT user_applications_application_id_fkey FOREIGN KEY (application_id) REFERENCES public.applications(id);


--
-- Name: user_applications user_applications_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.user_applications
    ADD CONSTRAINT user_applications_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id);


--
-- PostgreSQL database dump complete
--

