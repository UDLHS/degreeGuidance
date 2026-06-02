--
-- PostgreSQL database dump
--

\restrict aur4ZGjJLb2NqLbCQaJQUHDmN05d6D9y5hFdkmNj677e0iCkxEs6tdF25ATjKA0

-- Dumped from database version 16.14 (Ubuntu 16.14-1.pgdg26.04+1)
-- Dumped by pg_dump version 16.14 (Ubuntu 16.14-1.pgdg26.04+1)

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
-- Name: pgcrypto; Type: EXTENSION; Schema: -; Owner: -
--

CREATE EXTENSION IF NOT EXISTS pgcrypto WITH SCHEMA public;


--
-- Name: EXTENSION pgcrypto; Type: COMMENT; Schema: -; Owner: 
--

COMMENT ON EXTENSION pgcrypto IS 'cryptographic functions';


--
-- Name: vector; Type: EXTENSION; Schema: -; Owner: -
--

CREATE EXTENSION IF NOT EXISTS vector WITH SCHEMA public;


--
-- Name: EXTENSION vector; Type: COMMENT; Schema: -; Owner: 
--

COMMENT ON EXTENSION vector IS 'vector data type and ivfflat and hnsw access methods';


SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: alembic_version; Type: TABLE; Schema: public; Owner: degree_app
--

CREATE TABLE public.alembic_version (
    version_num character varying(32) NOT NULL
);


ALTER TABLE public.alembic_version OWNER TO degree_app;

--
-- Name: course_aliases; Type: TABLE; Schema: public; Owner: degree_app
--

CREATE TABLE public.course_aliases (
    alias_id integer NOT NULL,
    course_code character varying(15) NOT NULL,
    alias_text text NOT NULL,
    source character varying(50),
    confidence numeric(3,2),
    is_verified boolean DEFAULT false NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.course_aliases OWNER TO degree_app;

--
-- Name: course_aliases_alias_id_seq; Type: SEQUENCE; Schema: public; Owner: degree_app
--

CREATE SEQUENCE public.course_aliases_alias_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.course_aliases_alias_id_seq OWNER TO degree_app;

--
-- Name: course_aliases_alias_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: degree_app
--

ALTER SEQUENCE public.course_aliases_alias_id_seq OWNED BY public.course_aliases.alias_id;


--
-- Name: course_stream_eligibility; Type: TABLE; Schema: public; Owner: degree_app
--

CREATE TABLE public.course_stream_eligibility (
    course_code character varying(15) NOT NULL,
    stream_id integer NOT NULL
);


ALTER TABLE public.course_stream_eligibility OWNER TO degree_app;

--
-- Name: courses; Type: TABLE; Schema: public; Owner: degree_app
--

CREATE TABLE public.courses (
    course_code character varying(15) NOT NULL,
    course_number character varying(5),
    university_id integer NOT NULL,
    faculty_id integer,
    name_en character varying(300) NOT NULL,
    name_si character varying(400),
    name_ta character varying(400),
    degree_type character varying(50),
    duration_years numeric(3,1),
    selection_basis character varying(20) DEFAULT 'district_quota'::character varying NOT NULL,
    requires_aptitude_test boolean DEFAULT false NOT NULL,
    description text,
    career_outlook text,
    is_active boolean DEFAULT true NOT NULL,
    first_intake_year integer,
    metadata jsonb DEFAULT '{}'::jsonb NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL,
    CONSTRAINT ck_courses_selection_basis CHECK (((selection_basis)::text = ANY ((ARRAY['district_quota'::character varying, 'all_island_merit'::character varying])::text[])))
);


ALTER TABLE public.courses OWNER TO degree_app;

--
-- Name: COLUMN courses.selection_basis; Type: COMMENT; Schema: public; Owner: degree_app
--

COMMENT ON COLUMN public.courses.selection_basis IS 'Set via manual seed from handbook Section 1.1 and Section 9 markers. Not derived from cutoff CSV data — OCR does not capture the * marker.';


--
-- Name: COLUMN courses.requires_aptitude_test; Type: COMMENT; Schema: public; Owner: degree_app
--

COMMENT ON COLUMN public.courses.requires_aptitude_test IS 'Set via manual seed from handbook Section 9 # markers. Not derived from cutoff CSV data.';


--
-- Name: districts; Type: TABLE; Schema: public; Owner: degree_app
--

CREATE TABLE public.districts (
    district_id integer NOT NULL,
    code character varying(20) NOT NULL,
    name_en character varying(50) NOT NULL,
    name_si character varying(100),
    name_ta character varying(100),
    province character varying(50),
    is_disadvantaged boolean DEFAULT false NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.districts OWNER TO degree_app;

--
-- Name: districts_district_id_seq; Type: SEQUENCE; Schema: public; Owner: degree_app
--

CREATE SEQUENCE public.districts_district_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.districts_district_id_seq OWNER TO degree_app;

--
-- Name: districts_district_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: degree_app
--

ALTER SEQUENCE public.districts_district_id_seq OWNED BY public.districts.district_id;


--
-- Name: faculties; Type: TABLE; Schema: public; Owner: degree_app
--

CREATE TABLE public.faculties (
    faculty_id integer NOT NULL,
    university_id integer NOT NULL,
    name_en character varying(200) NOT NULL,
    short_name character varying(50),
    website_url text
);


ALTER TABLE public.faculties OWNER TO degree_app;

--
-- Name: faculties_faculty_id_seq; Type: SEQUENCE; Schema: public; Owner: degree_app
--

CREATE SEQUENCE public.faculties_faculty_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.faculties_faculty_id_seq OWNER TO degree_app;

--
-- Name: faculties_faculty_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: degree_app
--

ALTER SEQUENCE public.faculties_faculty_id_seq OWNED BY public.faculties.faculty_id;


--
-- Name: ingestion_runs; Type: TABLE; Schema: public; Owner: degree_app
--

CREATE TABLE public.ingestion_runs (
    run_id uuid DEFAULT gen_random_uuid() NOT NULL,
    run_type character varying(30) NOT NULL,
    source_label character varying(100),
    year integer,
    status character varying(20) NOT NULL,
    started_at timestamp with time zone DEFAULT now() NOT NULL,
    completed_at timestamp with time zone,
    records_processed integer,
    records_failed integer,
    triggered_by character varying(100),
    notes text,
    error_log text,
    CONSTRAINT chk_run_status CHECK (((status)::text = ANY ((ARRAY['running'::character varying, 'success'::character varying, 'failed'::character varying, 'partial'::character varying])::text[])))
);


ALTER TABLE public.ingestion_runs OWNER TO degree_app;

--
-- Name: mediums; Type: TABLE; Schema: public; Owner: degree_app
--

CREATE TABLE public.mediums (
    medium_id integer NOT NULL,
    code character varying(10) NOT NULL,
    name_en character varying(50) NOT NULL
);


ALTER TABLE public.mediums OWNER TO degree_app;

--
-- Name: mediums_medium_id_seq; Type: SEQUENCE; Schema: public; Owner: degree_app
--

CREATE SEQUENCE public.mediums_medium_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.mediums_medium_id_seq OWNER TO degree_app;

--
-- Name: mediums_medium_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: degree_app
--

ALTER SEQUENCE public.mediums_medium_id_seq OWNED BY public.mediums.medium_id;


--
-- Name: parse_errors; Type: TABLE; Schema: public; Owner: degree_app
--

CREATE TABLE public.parse_errors (
    error_id bigint NOT NULL,
    run_id uuid,
    source_label character varying(100),
    page_number integer,
    raw_block text,
    error_type character varying(50),
    error_message text,
    resolved boolean DEFAULT false NOT NULL,
    resolved_action text,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.parse_errors OWNER TO degree_app;

--
-- Name: parse_errors_error_id_seq; Type: SEQUENCE; Schema: public; Owner: degree_app
--

CREATE SEQUENCE public.parse_errors_error_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.parse_errors_error_id_seq OWNER TO degree_app;

--
-- Name: parse_errors_error_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: degree_app
--

ALTER SEQUENCE public.parse_errors_error_id_seq OWNED BY public.parse_errors.error_id;


--
-- Name: special_provision_categories; Type: TABLE; Schema: public; Owner: degree_app
--

CREATE TABLE public.special_provision_categories (
    category_id integer NOT NULL,
    code character varying(30) NOT NULL,
    name_en character varying(100) NOT NULL,
    description text,
    handbook_section character varying(20)
);


ALTER TABLE public.special_provision_categories OWNER TO degree_app;

--
-- Name: special_provision_categories_category_id_seq; Type: SEQUENCE; Schema: public; Owner: degree_app
--

CREATE SEQUENCE public.special_provision_categories_category_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.special_provision_categories_category_id_seq OWNER TO degree_app;

--
-- Name: special_provision_categories_category_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: degree_app
--

ALTER SEQUENCE public.special_provision_categories_category_id_seq OWNED BY public.special_provision_categories.category_id;


--
-- Name: stream_subjects; Type: TABLE; Schema: public; Owner: degree_app
--

CREATE TABLE public.stream_subjects (
    stream_id integer NOT NULL,
    subject_id integer NOT NULL
);


ALTER TABLE public.stream_subjects OWNER TO degree_app;

--
-- Name: streams; Type: TABLE; Schema: public; Owner: degree_app
--

CREATE TABLE public.streams (
    stream_id integer NOT NULL,
    code character varying(30) NOT NULL,
    name_en character varying(50) NOT NULL,
    name_si character varying(100),
    name_ta character varying(100),
    description text
);


ALTER TABLE public.streams OWNER TO degree_app;

--
-- Name: streams_stream_id_seq; Type: SEQUENCE; Schema: public; Owner: degree_app
--

CREATE SEQUENCE public.streams_stream_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.streams_stream_id_seq OWNER TO degree_app;

--
-- Name: streams_stream_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: degree_app
--

ALTER SEQUENCE public.streams_stream_id_seq OWNED BY public.streams.stream_id;


--
-- Name: subjects; Type: TABLE; Schema: public; Owner: degree_app
--

CREATE TABLE public.subjects (
    subject_id integer NOT NULL,
    code character varying(30) NOT NULL,
    name_en character varying(100) NOT NULL,
    name_si character varying(150),
    name_ta character varying(150),
    is_practical boolean DEFAULT false NOT NULL
);


ALTER TABLE public.subjects OWNER TO degree_app;

--
-- Name: subjects_subject_id_seq; Type: SEQUENCE; Schema: public; Owner: degree_app
--

CREATE SEQUENCE public.subjects_subject_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.subjects_subject_id_seq OWNER TO degree_app;

--
-- Name: subjects_subject_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: degree_app
--

ALTER SEQUENCE public.subjects_subject_id_seq OWNED BY public.subjects.subject_id;


--
-- Name: universities; Type: TABLE; Schema: public; Owner: degree_app
--

CREATE TABLE public.universities (
    university_id integer NOT NULL,
    code character varying(20) NOT NULL,
    name_en character varying(150) NOT NULL,
    name_si character varying(200),
    name_ta character varying(200),
    short_name character varying(50),
    district_id integer,
    website_url text,
    established integer,
    is_active boolean DEFAULT true NOT NULL
);


ALTER TABLE public.universities OWNER TO degree_app;

--
-- Name: universities_university_id_seq; Type: SEQUENCE; Schema: public; Owner: degree_app
--

CREATE SEQUENCE public.universities_university_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.universities_university_id_seq OWNER TO degree_app;

--
-- Name: universities_university_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: degree_app
--

ALTER SEQUENCE public.universities_university_id_seq OWNED BY public.universities.university_id;


--
-- Name: z_score_cutoffs; Type: TABLE; Schema: public; Owner: degree_app
--

CREATE TABLE public.z_score_cutoffs (
    cutoff_id bigint NOT NULL,
    year integer NOT NULL,
    course_code character varying(15) NOT NULL,
    district_id integer NOT NULL,
    z_score numeric(6,4),
    notes text,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.z_score_cutoffs OWNER TO degree_app;

--
-- Name: COLUMN z_score_cutoffs.year; Type: COMMENT; Schema: public; Owner: degree_app
--

COMMENT ON COLUMN public.z_score_cutoffs.year IS 'Academic year of the A/L examination that produced these cutoffs. NOT the handbook publication year. The 2024/2025 handbook contains year=2023 cutoffs (from A/L 2023).';


--
-- Name: COLUMN z_score_cutoffs.z_score; Type: COMMENT; Schema: public; Owner: degree_app
--

COMMENT ON COLUMN public.z_score_cutoffs.z_score IS 'Z-score range observed in handbook data: approximately [-0.7, +2.9]. Validator range: [-2.0, +3.0]. NULL = NQC (No Qualified Candidates).';


--
-- Name: z_score_cutoffs_cutoff_id_seq; Type: SEQUENCE; Schema: public; Owner: degree_app
--

CREATE SEQUENCE public.z_score_cutoffs_cutoff_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.z_score_cutoffs_cutoff_id_seq OWNER TO degree_app;

--
-- Name: z_score_cutoffs_cutoff_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: degree_app
--

ALTER SEQUENCE public.z_score_cutoffs_cutoff_id_seq OWNED BY public.z_score_cutoffs.cutoff_id;


--
-- Name: course_aliases alias_id; Type: DEFAULT; Schema: public; Owner: degree_app
--

ALTER TABLE ONLY public.course_aliases ALTER COLUMN alias_id SET DEFAULT nextval('public.course_aliases_alias_id_seq'::regclass);


--
-- Name: districts district_id; Type: DEFAULT; Schema: public; Owner: degree_app
--

ALTER TABLE ONLY public.districts ALTER COLUMN district_id SET DEFAULT nextval('public.districts_district_id_seq'::regclass);


--
-- Name: faculties faculty_id; Type: DEFAULT; Schema: public; Owner: degree_app
--

ALTER TABLE ONLY public.faculties ALTER COLUMN faculty_id SET DEFAULT nextval('public.faculties_faculty_id_seq'::regclass);


--
-- Name: mediums medium_id; Type: DEFAULT; Schema: public; Owner: degree_app
--

ALTER TABLE ONLY public.mediums ALTER COLUMN medium_id SET DEFAULT nextval('public.mediums_medium_id_seq'::regclass);


--
-- Name: parse_errors error_id; Type: DEFAULT; Schema: public; Owner: degree_app
--

ALTER TABLE ONLY public.parse_errors ALTER COLUMN error_id SET DEFAULT nextval('public.parse_errors_error_id_seq'::regclass);


--
-- Name: special_provision_categories category_id; Type: DEFAULT; Schema: public; Owner: degree_app
--

ALTER TABLE ONLY public.special_provision_categories ALTER COLUMN category_id SET DEFAULT nextval('public.special_provision_categories_category_id_seq'::regclass);


--
-- Name: streams stream_id; Type: DEFAULT; Schema: public; Owner: degree_app
--

ALTER TABLE ONLY public.streams ALTER COLUMN stream_id SET DEFAULT nextval('public.streams_stream_id_seq'::regclass);


--
-- Name: subjects subject_id; Type: DEFAULT; Schema: public; Owner: degree_app
--

ALTER TABLE ONLY public.subjects ALTER COLUMN subject_id SET DEFAULT nextval('public.subjects_subject_id_seq'::regclass);


--
-- Name: universities university_id; Type: DEFAULT; Schema: public; Owner: degree_app
--

ALTER TABLE ONLY public.universities ALTER COLUMN university_id SET DEFAULT nextval('public.universities_university_id_seq'::regclass);


--
-- Name: z_score_cutoffs cutoff_id; Type: DEFAULT; Schema: public; Owner: degree_app
--

ALTER TABLE ONLY public.z_score_cutoffs ALTER COLUMN cutoff_id SET DEFAULT nextval('public.z_score_cutoffs_cutoff_id_seq'::regclass);


--
-- Name: alembic_version alembic_version_pkc; Type: CONSTRAINT; Schema: public; Owner: degree_app
--

ALTER TABLE ONLY public.alembic_version
    ADD CONSTRAINT alembic_version_pkc PRIMARY KEY (version_num);


--
-- Name: course_aliases course_aliases_pkey; Type: CONSTRAINT; Schema: public; Owner: degree_app
--

ALTER TABLE ONLY public.course_aliases
    ADD CONSTRAINT course_aliases_pkey PRIMARY KEY (alias_id);


--
-- Name: course_stream_eligibility course_stream_eligibility_pkey; Type: CONSTRAINT; Schema: public; Owner: degree_app
--

ALTER TABLE ONLY public.course_stream_eligibility
    ADD CONSTRAINT course_stream_eligibility_pkey PRIMARY KEY (course_code, stream_id);


--
-- Name: courses courses_pkey; Type: CONSTRAINT; Schema: public; Owner: degree_app
--

ALTER TABLE ONLY public.courses
    ADD CONSTRAINT courses_pkey PRIMARY KEY (course_code);


--
-- Name: districts districts_code_key; Type: CONSTRAINT; Schema: public; Owner: degree_app
--

ALTER TABLE ONLY public.districts
    ADD CONSTRAINT districts_code_key UNIQUE (code);


--
-- Name: districts districts_pkey; Type: CONSTRAINT; Schema: public; Owner: degree_app
--

ALTER TABLE ONLY public.districts
    ADD CONSTRAINT districts_pkey PRIMARY KEY (district_id);


--
-- Name: faculties faculties_pkey; Type: CONSTRAINT; Schema: public; Owner: degree_app
--

ALTER TABLE ONLY public.faculties
    ADD CONSTRAINT faculties_pkey PRIMARY KEY (faculty_id);


--
-- Name: ingestion_runs ingestion_runs_pkey; Type: CONSTRAINT; Schema: public; Owner: degree_app
--

ALTER TABLE ONLY public.ingestion_runs
    ADD CONSTRAINT ingestion_runs_pkey PRIMARY KEY (run_id);


--
-- Name: mediums mediums_code_key; Type: CONSTRAINT; Schema: public; Owner: degree_app
--

ALTER TABLE ONLY public.mediums
    ADD CONSTRAINT mediums_code_key UNIQUE (code);


--
-- Name: mediums mediums_pkey; Type: CONSTRAINT; Schema: public; Owner: degree_app
--

ALTER TABLE ONLY public.mediums
    ADD CONSTRAINT mediums_pkey PRIMARY KEY (medium_id);


--
-- Name: parse_errors parse_errors_pkey; Type: CONSTRAINT; Schema: public; Owner: degree_app
--

ALTER TABLE ONLY public.parse_errors
    ADD CONSTRAINT parse_errors_pkey PRIMARY KEY (error_id);


--
-- Name: special_provision_categories special_provision_categories_code_key; Type: CONSTRAINT; Schema: public; Owner: degree_app
--

ALTER TABLE ONLY public.special_provision_categories
    ADD CONSTRAINT special_provision_categories_code_key UNIQUE (code);


--
-- Name: special_provision_categories special_provision_categories_pkey; Type: CONSTRAINT; Schema: public; Owner: degree_app
--

ALTER TABLE ONLY public.special_provision_categories
    ADD CONSTRAINT special_provision_categories_pkey PRIMARY KEY (category_id);


--
-- Name: stream_subjects stream_subjects_pkey; Type: CONSTRAINT; Schema: public; Owner: degree_app
--

ALTER TABLE ONLY public.stream_subjects
    ADD CONSTRAINT stream_subjects_pkey PRIMARY KEY (stream_id, subject_id);


--
-- Name: streams streams_code_key; Type: CONSTRAINT; Schema: public; Owner: degree_app
--

ALTER TABLE ONLY public.streams
    ADD CONSTRAINT streams_code_key UNIQUE (code);


--
-- Name: streams streams_pkey; Type: CONSTRAINT; Schema: public; Owner: degree_app
--

ALTER TABLE ONLY public.streams
    ADD CONSTRAINT streams_pkey PRIMARY KEY (stream_id);


--
-- Name: subjects subjects_code_key; Type: CONSTRAINT; Schema: public; Owner: degree_app
--

ALTER TABLE ONLY public.subjects
    ADD CONSTRAINT subjects_code_key UNIQUE (code);


--
-- Name: subjects subjects_pkey; Type: CONSTRAINT; Schema: public; Owner: degree_app
--

ALTER TABLE ONLY public.subjects
    ADD CONSTRAINT subjects_pkey PRIMARY KEY (subject_id);


--
-- Name: universities universities_code_key; Type: CONSTRAINT; Schema: public; Owner: degree_app
--

ALTER TABLE ONLY public.universities
    ADD CONSTRAINT universities_code_key UNIQUE (code);


--
-- Name: universities universities_pkey; Type: CONSTRAINT; Schema: public; Owner: degree_app
--

ALTER TABLE ONLY public.universities
    ADD CONSTRAINT universities_pkey PRIMARY KEY (university_id);


--
-- Name: course_aliases uq_alias_per_course; Type: CONSTRAINT; Schema: public; Owner: degree_app
--

ALTER TABLE ONLY public.course_aliases
    ADD CONSTRAINT uq_alias_per_course UNIQUE (alias_text, course_code);


--
-- Name: faculties uq_faculty_per_university; Type: CONSTRAINT; Schema: public; Owner: degree_app
--

ALTER TABLE ONLY public.faculties
    ADD CONSTRAINT uq_faculty_per_university UNIQUE (university_id, name_en);


--
-- Name: z_score_cutoffs uq_zscore_year_course_district; Type: CONSTRAINT; Schema: public; Owner: degree_app
--

ALTER TABLE ONLY public.z_score_cutoffs
    ADD CONSTRAINT uq_zscore_year_course_district UNIQUE (year, course_code, district_id);


--
-- Name: z_score_cutoffs z_score_cutoffs_pkey; Type: CONSTRAINT; Schema: public; Owner: degree_app
--

ALTER TABLE ONLY public.z_score_cutoffs
    ADD CONSTRAINT z_score_cutoffs_pkey PRIMARY KEY (cutoff_id);


--
-- Name: idx_aliases_course; Type: INDEX; Schema: public; Owner: degree_app
--

CREATE INDEX idx_aliases_course ON public.course_aliases USING btree (course_code);


--
-- Name: idx_aliases_text; Type: INDEX; Schema: public; Owner: degree_app
--

CREATE INDEX idx_aliases_text ON public.course_aliases USING gin (to_tsvector('english'::regconfig, alias_text));


--
-- Name: idx_courses_active; Type: INDEX; Schema: public; Owner: degree_app
--

CREATE INDEX idx_courses_active ON public.courses USING btree (is_active) WHERE (is_active = true);


--
-- Name: idx_courses_number; Type: INDEX; Schema: public; Owner: degree_app
--

CREATE INDEX idx_courses_number ON public.courses USING btree (course_number);


--
-- Name: idx_courses_selection_basis; Type: INDEX; Schema: public; Owner: degree_app
--

CREATE INDEX idx_courses_selection_basis ON public.courses USING btree (selection_basis);


--
-- Name: idx_courses_university; Type: INDEX; Schema: public; Owner: degree_app
--

CREATE INDEX idx_courses_university ON public.courses USING btree (university_id);


--
-- Name: idx_parse_errors_run; Type: INDEX; Schema: public; Owner: degree_app
--

CREATE INDEX idx_parse_errors_run ON public.parse_errors USING btree (run_id, resolved);


--
-- Name: idx_zscore_course_history; Type: INDEX; Schema: public; Owner: degree_app
--

CREATE INDEX idx_zscore_course_history ON public.z_score_cutoffs USING btree (course_code, year);


--
-- Name: idx_zscore_district_lookup; Type: INDEX; Schema: public; Owner: degree_app
--

CREATE INDEX idx_zscore_district_lookup ON public.z_score_cutoffs USING btree (year, district_id, z_score) WHERE (z_score IS NOT NULL);


--
-- Name: course_aliases course_aliases_course_code_fkey; Type: FK CONSTRAINT; Schema: public; Owner: degree_app
--

ALTER TABLE ONLY public.course_aliases
    ADD CONSTRAINT course_aliases_course_code_fkey FOREIGN KEY (course_code) REFERENCES public.courses(course_code) ON DELETE CASCADE;


--
-- Name: course_stream_eligibility course_stream_eligibility_course_code_fkey; Type: FK CONSTRAINT; Schema: public; Owner: degree_app
--

ALTER TABLE ONLY public.course_stream_eligibility
    ADD CONSTRAINT course_stream_eligibility_course_code_fkey FOREIGN KEY (course_code) REFERENCES public.courses(course_code) ON DELETE CASCADE;


--
-- Name: course_stream_eligibility course_stream_eligibility_stream_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: degree_app
--

ALTER TABLE ONLY public.course_stream_eligibility
    ADD CONSTRAINT course_stream_eligibility_stream_id_fkey FOREIGN KEY (stream_id) REFERENCES public.streams(stream_id);


--
-- Name: courses courses_faculty_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: degree_app
--

ALTER TABLE ONLY public.courses
    ADD CONSTRAINT courses_faculty_id_fkey FOREIGN KEY (faculty_id) REFERENCES public.faculties(faculty_id) ON DELETE SET NULL;


--
-- Name: courses courses_university_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: degree_app
--

ALTER TABLE ONLY public.courses
    ADD CONSTRAINT courses_university_id_fkey FOREIGN KEY (university_id) REFERENCES public.universities(university_id) ON DELETE RESTRICT;


--
-- Name: faculties faculties_university_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: degree_app
--

ALTER TABLE ONLY public.faculties
    ADD CONSTRAINT faculties_university_id_fkey FOREIGN KEY (university_id) REFERENCES public.universities(university_id) ON DELETE CASCADE;


--
-- Name: parse_errors parse_errors_run_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: degree_app
--

ALTER TABLE ONLY public.parse_errors
    ADD CONSTRAINT parse_errors_run_id_fkey FOREIGN KEY (run_id) REFERENCES public.ingestion_runs(run_id) ON DELETE CASCADE;


--
-- Name: stream_subjects stream_subjects_stream_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: degree_app
--

ALTER TABLE ONLY public.stream_subjects
    ADD CONSTRAINT stream_subjects_stream_id_fkey FOREIGN KEY (stream_id) REFERENCES public.streams(stream_id) ON DELETE CASCADE;


--
-- Name: stream_subjects stream_subjects_subject_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: degree_app
--

ALTER TABLE ONLY public.stream_subjects
    ADD CONSTRAINT stream_subjects_subject_id_fkey FOREIGN KEY (subject_id) REFERENCES public.subjects(subject_id) ON DELETE CASCADE;


--
-- Name: universities universities_district_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: degree_app
--

ALTER TABLE ONLY public.universities
    ADD CONSTRAINT universities_district_id_fkey FOREIGN KEY (district_id) REFERENCES public.districts(district_id) ON DELETE SET NULL;


--
-- Name: z_score_cutoffs z_score_cutoffs_course_code_fkey; Type: FK CONSTRAINT; Schema: public; Owner: degree_app
--

ALTER TABLE ONLY public.z_score_cutoffs
    ADD CONSTRAINT z_score_cutoffs_course_code_fkey FOREIGN KEY (course_code) REFERENCES public.courses(course_code) ON DELETE RESTRICT;


--
-- Name: z_score_cutoffs z_score_cutoffs_district_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: degree_app
--

ALTER TABLE ONLY public.z_score_cutoffs
    ADD CONSTRAINT z_score_cutoffs_district_id_fkey FOREIGN KEY (district_id) REFERENCES public.districts(district_id) ON DELETE RESTRICT;


--
-- PostgreSQL database dump complete
--

\unrestrict aur4ZGjJLb2NqLbCQaJQUHDmN05d6D9y5hFdkmNj677e0iCkxEs6tdF25ATjKA0

