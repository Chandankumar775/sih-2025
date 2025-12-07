-- Create role enum for WatchTower users
CREATE TYPE public.app_role AS ENUM ('reporter', 'analyst', 'admin');

-- Create incident type enum
CREATE TYPE public.incident_type AS ENUM ('url', 'message', 'file');

-- Create severity enum
CREATE TYPE public.severity_level AS ENUM ('critical', 'high', 'medium', 'low');

-- Create incident status enum
CREATE TYPE public.incident_status AS ENUM ('pending', 'reviewed', 'escalated', 'resolved');

-- Create profiles table for user information
CREATE TABLE public.profiles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE NOT NULL UNIQUE,
    full_name TEXT,
    unit TEXT,
    location TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL
);

-- Create user_roles table for role-based access control
CREATE TABLE public.user_roles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE NOT NULL,
    role app_role NOT NULL DEFAULT 'reporter',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
    UNIQUE (user_id, role)
);

-- Create incidents table
CREATE TABLE public.incidents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    incident_id TEXT NOT NULL UNIQUE,
    user_id UUID REFERENCES auth.users(id) ON DELETE SET NULL,
    type incident_type NOT NULL,
    content TEXT,
    file_url TEXT,
    description TEXT,
    location TEXT,
    risk_score INTEGER DEFAULT 0 CHECK (risk_score >= 0 AND risk_score <= 100),
    severity severity_level DEFAULT 'low',
    status incident_status DEFAULT 'pending',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL
);

-- Create incident_analysis table for AI analysis results
CREATE TABLE public.incident_analysis (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    incident_id UUID REFERENCES public.incidents(id) ON DELETE CASCADE NOT NULL UNIQUE,
    summary TEXT,
    indicators JSONB DEFAULT '[]'::JSONB,
    recommendations JSONB DEFAULT '[]'::JSONB,
    iocs JSONB DEFAULT '[]'::JSONB,
    analyzed_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL
);

-- Enable Row Level Security
ALTER TABLE public.profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.user_roles ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.incidents ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.incident_analysis ENABLE ROW LEVEL SECURITY;

-- Security definer function to check user role
CREATE OR REPLACE FUNCTION public.has_role(_user_id UUID, _role app_role)
RETURNS BOOLEAN
LANGUAGE sql
STABLE
SECURITY DEFINER
SET search_path = public
AS $$
    SELECT EXISTS (
        SELECT 1
        FROM public.user_roles
        WHERE user_id = _user_id
          AND role = _role
    )
$$;

-- Function to check if user is analyst or admin
CREATE OR REPLACE FUNCTION public.is_analyst_or_admin(_user_id UUID)
RETURNS BOOLEAN
LANGUAGE sql
STABLE
SECURITY DEFINER
SET search_path = public
AS $$
    SELECT EXISTS (
        SELECT 1
        FROM public.user_roles
        WHERE user_id = _user_id
          AND role IN ('analyst', 'admin')
    )
$$;

-- RLS Policies for profiles
CREATE POLICY "Users can view their own profile"
ON public.profiles FOR SELECT
TO authenticated
USING (auth.uid() = user_id);

CREATE POLICY "Users can update their own profile"
ON public.profiles FOR UPDATE
TO authenticated
USING (auth.uid() = user_id);

CREATE POLICY "Users can insert their own profile"
ON public.profiles FOR INSERT
TO authenticated
WITH CHECK (auth.uid() = user_id);

-- RLS Policies for user_roles
CREATE POLICY "Users can view their own roles"
ON public.user_roles FOR SELECT
TO authenticated
USING (auth.uid() = user_id);

CREATE POLICY "Admins can manage all roles"
ON public.user_roles FOR ALL
TO authenticated
USING (public.has_role(auth.uid(), 'admin'));

-- RLS Policies for incidents
CREATE POLICY "Reporters can view their own incidents"
ON public.incidents FOR SELECT
TO authenticated
USING (auth.uid() = user_id);

CREATE POLICY "Analysts and admins can view all incidents"
ON public.incidents FOR SELECT
TO authenticated
USING (public.is_analyst_or_admin(auth.uid()));

CREATE POLICY "Authenticated users can create incidents"
ON public.incidents FOR INSERT
TO authenticated
WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Analysts and admins can update incidents"
ON public.incidents FOR UPDATE
TO authenticated
USING (public.is_analyst_or_admin(auth.uid()));

-- RLS Policies for incident_analysis
CREATE POLICY "Users can view analysis of their incidents"
ON public.incident_analysis FOR SELECT
TO authenticated
USING (
    EXISTS (
        SELECT 1 FROM public.incidents
        WHERE incidents.id = incident_analysis.incident_id
        AND incidents.user_id = auth.uid()
    )
);

CREATE POLICY "Analysts and admins can view all analysis"
ON public.incident_analysis FOR SELECT
TO authenticated
USING (public.is_analyst_or_admin(auth.uid()));

CREATE POLICY "Analysts and admins can create analysis"
ON public.incident_analysis FOR INSERT
TO authenticated
WITH CHECK (public.is_analyst_or_admin(auth.uid()));

-- Function to auto-create profile on user signup
CREATE OR REPLACE FUNCTION public.handle_new_user()
RETURNS TRIGGER
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = public
AS $$
BEGIN
    INSERT INTO public.profiles (user_id, full_name)
    VALUES (NEW.id, NEW.raw_user_meta_data->>'full_name');
    
    -- Default role is reporter
    INSERT INTO public.user_roles (user_id, role)
    VALUES (NEW.id, 'reporter');
    
    RETURN NEW;
END;
$$;

-- Trigger for auto-creating profile
CREATE TRIGGER on_auth_user_created
    AFTER INSERT ON auth.users
    FOR EACH ROW EXECUTE FUNCTION public.handle_new_user();

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION public.update_updated_at_column()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$;

-- Triggers for updated_at
CREATE TRIGGER update_profiles_updated_at
    BEFORE UPDATE ON public.profiles
    FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();

CREATE TRIGGER update_incidents_updated_at
    BEFORE UPDATE ON public.incidents
    FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();