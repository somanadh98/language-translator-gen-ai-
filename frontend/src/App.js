import React, {useState} from 'react';

export default function App(){
  const [text, setText] = useState('Hello world');
  const [tgt, setTgt] = useState('fra_Latn');
  const [result, setResult] = useState('');
  const [loading, setLoading] = useState(false);

  async function doTranslate(e){
    e.preventDefault();
    setLoading(true);
    setResult('');
    try{
      const res = await fetch('/translate', {
        method: 'POST',
        headers: {'Content-Type':'application/json'},
        body: JSON.stringify({text, tgt_lang: tgt})
      });
      const data = await res.json();
      if(res.ok){
        setResult(data.translated_text);
      } else {
        setResult('Error: ' + (data.detail || JSON.stringify(data)));
      }
    }catch(err){
      setResult('Request failed: ' + err.message);
    }finally{
      setLoading(false);
    }
  }

  return (<div style={{maxWidth:800, margin:'40px auto', fontFamily:'Arial'}}>
    <h1>Multilingual Translator</h1>
    <form onSubmit={doTranslate}>
      <div style={{marginBottom:10}}>
        <label>Text</label><br/>
        <textarea value={text} onChange={e=>setText(e.target.value)} rows={6} style={{width:'100%'}}/>
      </div>
      <div style={{marginBottom:10}}>
        <label>Target language (NLLB code, e.g. fra_Latn)</label><br/>
        <input value={tgt} onChange={e=>setTgt(e.target.value)} style={{width:'100%'}}/>
      </div>
      <button type='submit' disabled={loading}>{loading ? 'Translating...' : 'Translate'}</button>
    </form>
    <h3>Result</h3>
    <pre style={{whiteSpace:'pre-wrap', background:'#f6f6f6', padding:10}}>{result}</pre>
  </div>)
}
