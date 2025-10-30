import pandas as pd
from glob import glob
from logger import Logger
import os
import re


# TODO: modify columns
# TODO: count number of matches for each player (if below a threshold, delete data for player)


class DataCleaning:
    def __init__(self, logger: Logger, filepath: str):
        self.logger = logger
        self.filepath = filepath

        # columns to exclude from each file
        self.drop_columns = ['Op.eK-eD', 'eKAST', 'eK(hs)', 'eD(t)', 'eADR', 'KAST.1', 'eKAST.1', '1', '2', '3', '4', '5']

    def second_stage_df(self, df: pd.DataFrame):
        df['Op.K-D'] = df['Op.K-D'].apply(self._modify_opk)
        cols = ['K(hs)', 'A(f)', 'D(t)']
        for col in cols:
            if col != 'A(f)':
                new_col = re.search(r'\(([a-z]+)\)', col).group(1)
                df[new_col] = df[col].apply(self._modify_kad)

            df[re.sub(r'\([a-z]+\)', '', col)] = df[col].apply(self._modify_kad_exclude)

        df = df.drop(cols, axis=1)
        return df

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

    @staticmethod
    def _modify_opk(op_kd: str):
        value = op_kd.split(' : ')
        return int(value[0]) - int(value[1])

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
