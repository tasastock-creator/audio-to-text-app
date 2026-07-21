const corsHeaders = {
  'Access-Control-Allow-Origin': 'https://tasastock-creator.github.io',
  'Access-Control-Allow-Methods': 'POST,OPTIONS,GET',
  'Access-Control-Allow-Headers': 'Content-Type',
};

function json(data, status = 200) {
  return new Response(JSON.stringify(data), {
    status,
    headers: { ...corsHeaders, 'Content-Type': 'application/json; charset=utf-8' },
  });
}

function toBase64(bytes) {
  let binary = '';
  const chunk = 0x8000;
  for (let i = 0; i <