from bs4 import BeautifulSoup
import requests
import urllib.parse


def get_stop_info(stop_id):
    post_params = {
        '__EVENTTARGET': '',
        '__EVENTARGUMENT': '',
        '__LASTFOCUS': '',
        'lng': 'es-ES',
        'p$lt$ctl00$CajaBusqueda$txtWord_exWatermark_ClientState': '',
        'p$lt$ctl00$CajaBusqueda$txtWord': '',
        'p$lt$ctl04$Contenido$p$lt$ctl02$TiempoDeEspera_caja$btTiempoEsperaParada': 'Aceptar',
        'p$lt$ctl04$Contenido$p$lt$ctl02$TiempoEsperaLineaParada$cbLineas': ''
    }

    session = requests.Session()

    page = session.get("https://www.emtmadrid.es/EMTBUS/MiBus.aspx")
    soup = BeautifulSoup(page.content, 'html.parser')

    state = soup.select('input#__VIEWSTATE')[0].get('value')
    state_generator = soup.select('input#__VIEWSTATEGENERATOR')[0].get('value')

    scripts = soup.select('script')
    script_src = None
    for s in scripts:
        if s.get('src') and 'manScript_HiddenField' in s.get('src'):
            script_src = s.get('src')
            break

    man_script = urllib.parse.unquote(script_src).split('_TSM_CombinedScripts_=')[-1]


    post_params['__VIEWSTATE'] = state
    post_params['__VIEWSTATEGENERATOR'] = state_generator
    post_params['p$lt$ctl04$Contenido$p$lt$ctl02$TiempoDeEspera_caja$txtParada'] = stop_id
    post_params['manScript_HiddenField'] = man_script


    res = session.post('https://www.emtmadrid.es/EMTBUS/MiBus.aspx', data=post_params)
    sopt_url_part = res.text.split('window.open("..')[1].split('", "_blank')[0]

    stop_page = session.get(f'https://www.emtmadrid.es{sopt_url_part}')
    soup = BeautifulSoup(stop_page.content, 'html.parser')


    data = []
    table = soup.select('table.table')[0]
    table_body = table.find('tbody')

    rows = table_body.find_all('tr')
    for row in rows:
        cols = row.find_all('td')
        cols = [ele.text.strip() for ele in cols]
        data.append({
            'line': cols[0],
            'destination': cols[1],
            'arrival': cols[2]
        })

    return data


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='Get bus stop info.')
    parser.add_argument('bus_stop', metavar='Bus stop', type=int,
                        help='Bus stop number')

    args = parser.parse_args()

    print(get_stop_info(args.bus_stop))
else:
    from flask import Flask, jsonify, render_template
    app = Flask(__name__)

    @app.route('/')
    def root():
        return render_template('index.html')

    @app.route('/<stop>')
    def stop_info(stop):
        try:
            return render_template('stop.html', stops=get_stop_info(stop))
        except Exception as e:
            return render_template('index.html', error='Error :(')
