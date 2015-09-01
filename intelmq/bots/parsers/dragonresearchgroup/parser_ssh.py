# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import sys

from intelmq.lib import utils
from intelmq.lib.bot import Bot
from intelmq.lib.message import Event


class DragonResearchGroupSSHParserBot(Bot):

    def process(self):
        report = self.receive_message()

        if report is None or not report.contains("raw"):
            self.acknowledge_message()
            return

        raw_report = utils.base64_decode(report.value("raw"))
        for row in raw_report.splitlines():

            row = row.strip()

            if len(row) == 0 or row.startswith('#'):
                continue

            splitted_row = row.split('|')
            event = Event()

            columns = ["source.asn", "source.as_name",
                       "source.ip", "time.source"]

            for key, value in zip(columns, splitted_row):
                value = value.strip()

                if key == "time.source":
                    value += "T00:00:00+00:00"

                event.add(key, value, sanitize=True)

            event.add('time.observation', report.value(
                'time.observation'), sanitize=True)
            event.add('feed.name', report.value("feed.name"))
            event.add('feed.url', report.value("feed.url"))
            event.add('classification.type', u'brute-force')
            event.add('protocol.application', u'ssh')
            event.add("raw", row, sanitize=True)

            self.send_message(event)
        self.acknowledge_message()


if __name__ == "__main__":
    bot = DragonResearchGroupSSHParserBot(sys.argv[1])
    bot.start()