from pathlib import Path
from tempfile import NamedTemporaryFile, TemporaryDirectory

import gradio as gr

if gr.NO_RELOAD:
    import pandas as pd

    import pdf_parsing


def upload_pdf(file: str):
    df = pdf_parsing.parse_pdf(file)
    teams = sorted(df["Home"].unique())
    index = None
    for team in teams:
        if "arcella" in team.lower():
            index = team
            break
    team_selector = gr.Dropdown(choices=teams, value=index, interactive=True)
    calendar_df = filter_teams(df, index)
    return df, calendar_df, team_selector


def filter_teams(df: pd.DataFrame, team: str | None):
    if team is not None:
        df = df.loc[(df["Home"] == team) | (df["Away"] == team)].reset_index(drop=True)
        df = df.set_index([[i + 1 for i in range(len(df))]])
    return df


def download_calendar(df: pd.DataFrame):
    with TemporaryDirectory(delete=False) as tmp:
        fname = Path(tmp) / "calendar.csv"
        df.to_csv(fname, index=False)
        return gr.File(value=str(fname), visible=True)


with gr.Blocks() as demo:
    df_games = gr.State(pd.DataFrame())
    with gr.Row():
        with gr.Column(scale=4):
            gr.Markdown("# Arcella Basket Utilities")
        with gr.Column(scale=1):
            file_uploader = gr.UploadButton(file_types=[".pdf"])

    with gr.Row():
        team_selector = gr.Dropdown()

    with gr.Row():
        with gr.Column(scale=4):
            calendar_df = gr.DataFrame()
            with gr.Row():
                with gr.Column(scale=1):
                    download_btn = gr.DownloadButton()
                with gr.Column(scale=1):
                    file_downloader = gr.File(interactive=False, visible=False)
        with gr.Column(scale=1):
            rename_df = gr.DataFrame()

    file_uploader.upload(
        upload_pdf,
        inputs=[file_uploader],
        outputs=[df_games, calendar_df, team_selector],
    )

    team_selector.input(
        filter_teams, inputs=[df_games, team_selector], outputs=[calendar_df]
    )

    calendar_df.change(
        lambda: gr.File(interactive=False, visible=False),
        inputs=None,
        outputs=file_downloader,
    )

    download_btn.click(
        download_calendar, inputs=[calendar_df], outputs=[file_downloader]
    )


if __name__ == "__main__":
    demo.launch(share=False)
