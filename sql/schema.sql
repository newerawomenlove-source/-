create table if not exists public.users (
  tg_user_id bigint primary key,
  username text,
  first_name text,
  phone_number text,
  status text not null default 'started',
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create table if not exists public.funnel_answers (
  id bigint generated always as identity primary key,
  tg_user_id bigint not null references public.users(tg_user_id),
  selected_options text[] not null default '{}',
  custom_text text,
  created_at timestamptz not null default now()
);

create table if not exists public.events (
  id bigint generated always as identity primary key,
  tg_user_id bigint not null references public.users(tg_user_id),
  event_type text not null,
  payload jsonb,
  created_at timestamptz not null default now()
);

create table if not exists public.moderation_queue (
  id bigint generated always as identity primary key,
  tg_user_id bigint not null references public.users(tg_user_id),
  username text,
  first_name text,
  chat_id bigint not null,
  message_thread_id bigint,
  content_type text not null,
  text text,
  photo_file_id text,
  status text not null default 'pending',
  created_at timestamptz not null default now(),
  resolved_at timestamptz
);

create index if not exists events_tg_user_id_idx on public.events (tg_user_id);
create index if not exists events_event_type_idx on public.events (event_type);
create index if not exists funnel_answers_tg_user_id_idx on public.funnel_answers (tg_user_id);
create index if not exists moderation_queue_status_idx on public.moderation_queue (status);
