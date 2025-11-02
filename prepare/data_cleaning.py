import pandas as pd
from glob import glob
from logger import Logger
import os
import re


# TODO: standardize numeric features
# TODO: PCA? and then cluster?


class DataCleaning:
    def __init__(self, logger: Logger, filepath: str):
        self.logger = logger
        self.filepath = filepath
        self.threshold_matches = 1

        # columns to exclude
        self.drop_columns = ['Op.eK-eD', 'eKAST', 'eK(hs)', 'eD(t)', 'eADR', 'KAST.1', 'eKAST.1', '1', '2', '3', '4', '5']
        # columns to keep; I won't keep the team for now, because some players might have changed teams in the meantime so it can be noisy
        self.keep_columns = ['players', 'KAST', 'ADR', 'Swing', 'hs', 'opk', 'opd', '1vsX']

    def third_stage_df(self):
        df = self.second_stage_df().copy()

        # filtering to keep only the players with more than a certain amount of matches
        match_counts = df['players'].value_counts()
        players_with_enough_matches = match_counts[match_counts >= self.threshold_matches].index
        df_filtered = df[df['players'].isin(players_with_enough_matches)]

        # average numeric features per player; the clustering will represent the players styles
        player_means = df_filtered.groupby('players').mean(numeric_only=True).reset_index()
        return player_means

    def second_stage_df(self):
        df = self.first_stage_df().copy()

        cols = ['K(hs)', 'A(f)', 'D(t)']
        for col in cols:
            if col != 'A(f)':
                new_col = re.search(r'\(([a-z]+)\)', col).group(1)
                df[new_col] = df[col].apply(self._modify_kad)

            df[re.sub(r'\([a-z]+\)', '', col)] = df[col].apply(self._modify_kad_exclude)

        df[['opk', 'opd']] = df['Op.K-D'].str.split(' : ', n=1, expand=True).astype(int)
        df['opk'] = df.apply(lambda r: r['opk'] / r['K'] if r['K'] != 0 else 0, axis=1)
        df['opd'] = df.apply(lambda r: r['opd'] / r['D'] if r['D'] != 0 else 0, axis=1)

        df['KAST'] = df['KAST'].apply(self._modify_perc_columns)
        df['Swing'] = df['Swing'].apply(self._modify_perc_columns)

        return df[self.keep_columns]

    @staticmethod
    def _modify_perc_columns(value: str):
        value = re.sub(r'\+|-|%', '', value)
        return float(value) / 100

    @staticmethod
    def _modify_kad_exclude(value: str):
        value = re.sub(r'\(\d+\)', '', value)
        return int(value)

    @staticmethod
    def _modify_kad(value: str):
        groups = re.search(r'(\d+)\((\d+)', value)
        g1 = int(groups.group(1))
        g2 = int(groups.group(2))
        return (g2 / g1) if g1 != 0 else 0

    def first_stage_df(self):
        files = glob(os.path.join(self.filepath, r'*.csv'))
        if len(files) == 0:
            self.logger.log(f'ERROR: No .csv files in the folder {self.filepath}')
            return

        dfs = [self.read_dataframe(file, match_number) for match_number, file in enumerate(files)]
        df = pd.concat(dfs, ignore_index=True)
        df = df.dropna(subset=['Rating3.0']).drop(self.drop_columns, axis=1, errors='ignore')
        return df

    def read_dataframe(self, filename: str, match_number: int):
        """
        Op.K-D: Opening kills:death
        MKs: Rounds with two or more kills
        KAST: Percentage of rounds in which the player either had a kill, assist, survived or was traded
        1vsX: Clutches won
        K(hs): Kills (headshots)
        A(f): Assists (flash assists)
        D(t): Death (traded)
        ADR: Average damage per round
        Swing: How much, on average, a player change their team's chances of winning a round based on team economy, side, kills, deaths, damage, trading, and flash assists
        Rating3.0: Overall performance score for the match
        """

        self.logger.log(f'Opening {filename}...')

        df = pd.read_csv(filename)
        df['match'] = match_number
        df = df.rename(columns={'OpK-D': 'Op.K-D'})
        return df



""" teste """
logger = Logger()
dc = DataCleaning(logger, r'C:\Data\hltv\test')

df1 = dc.third_stage_df()
print()
