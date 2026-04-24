def load_css():
    return """
    <style>
    .block-container { padding-top: 1rem !important; }

    .titulo-secao { text-align: center; color: #2563eb; font-size: 18px; font-weight: 700; }
    .score { text-align: center; font-size: 40px; font-weight: 700; }

    table {
        margin-left: auto;
        margin-right: auto;
        font-size: 13px;
        text-align: center;
        border-collapse: collapse;
        width: 450px;
    }

    th { background-color: #2563eb; color: white; padding: 8px; }
    td { padding: 8px; border-bottom: 1px solid #eee; }

    .val-pos { color: #16a34a; font-weight: 800; }
    .val-neg { color: #dc2626; font-weight: 800; }
    </style>
    """