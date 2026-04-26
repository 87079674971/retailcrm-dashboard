create table if not exists public.orders (
  retailcrm_id bigint primary key,
  external_id text unique,
  order_number text,
  status text,
  first_name text,
  last_name text,
  phone text,
  email text,
  city text,
  address_text text,
  order_total numeric(12, 2) not null default 0,
  item_count integer not null default 0,
  utm_source text,
  order_type text,
  order_method text,
  currency text default 'KZT',
  retailcrm_created_at timestamptz,
  retailcrm_updated_at timestamptz,
  items jsonb not null default '[]'::jsonb,
  raw jsonb not null default '{}'::jsonb,
  synced_at timestamptz not null default now()
);

create index if not exists orders_created_at_idx on public.orders (retailcrm_created_at desc);
create index if not exists orders_city_idx on public.orders (city);
create index if not exists orders_total_idx on public.orders (order_total desc);

create table if not exists public.telegram_notifications (
  retailcrm_id bigint primary key references public.orders (retailcrm_id) on delete cascade,
  order_total numeric(12, 2) not null,
  message_text text not null,
  telegram_chat_id text not null,
  telegram_message_id bigint,
  sent_at timestamptz not null default now()
);

create or replace view public.orders_daily as
select
  date_trunc('day', retailcrm_created_at) as day,
  count(*) as orders_count,
  coalesce(sum(order_total), 0) as revenue
from public.orders
group by 1
order by 1 desc;
