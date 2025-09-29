
import React, { useMemo } from "react";
import "./GamesCalendar.css";
import matchDatesRaw from "./data/szge_match_dates.json";

const levels = ["#161b22", "#0e4429", "#006d32", "#26a641", "#39d353"];
const months = ["Sep", "Oct", "Nov", "Dec", "Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep"];
const weekdayLabels = ["", "Mon", "", "Wed", "", "Fri", ""];

function getDayKey(ts: number) {
    // Convert ms timestamp to YYYY-MM-DD string
    const d = new Date(ts);
    return d.toISOString().slice(0, 10);
}

function getYearStartEnd(latestTimestamp: number) {
    // Get the start and end timestamps for the latest year
    const end = latestTimestamp;
    const endDate = new Date(end);
    const startDate = new Date(endDate);
    startDate.setFullYear(endDate.getFullYear() - 1);
    return { start: startDate.getTime(), end };
}

function groupGamesByDay(matchDates: Record<string, number>, yearStart: number, yearEnd: number) {
    // Filter matches to the latest year, group by day
    const days: Record<string, number> = {};
    Object.values(matchDates).forEach(ts => {
        if (ts >= yearStart && ts <= yearEnd) {
            const key = getDayKey(ts);
            days[key] = (days[key] || 0) + 1;
        }
    });
    return days;
}

function buildCalendarGrid(dayCounts: Record<string, number>, yearStart: number) {
    // Build a 53x7 grid (weeks x days), each cell is games played that day
    const grid: number[][] = [];
    const dayKeys: string[] = [];
    let maxGames = 0;
    let date = new Date(yearStart);
    // Find the first Sunday before or on yearStart
    while (date.getDay() !== 0) {
        date.setDate(date.getDate() - 1);
    }
    for (let w = 0; w < 53; w++) {
        const week: number[] = [];
        for (let d = 0; d < 7; d++) {
            const key = getDayKey(date.getTime());
            const count = dayCounts[key] || 0;
            week.push(count);
            dayKeys.push(key);
            if (count > maxGames) maxGames = count;
            date.setDate(date.getDate() + 1);
        }
        grid.push(week);
    }
    return { grid, maxGames, dayKeys };
}

function getLevel(count: number, max: number) {
    if (max === 0) return 0;
    const percent = count / max;
    if (percent === 0) return 0;
    if (percent < 0.25) return 1;
    if (percent < 0.5) return 2;
    if (percent < 0.75) return 3;
    return 4;
}

export default function GamesCalendar() {
    // Memoize processing for performance
    const { grid, maxGames, totalGames } = useMemo(() => {
        const matchDates: Record<string, number> = matchDatesRaw;
        const allTimestamps = Object.values(matchDates);
        const latestTimestamp = Math.max(...allTimestamps);
        const { start, end } = getYearStartEnd(latestTimestamp);
        const dayCounts = groupGamesByDay(matchDates, start, end);
        const { grid, maxGames } = buildCalendarGrid(dayCounts, start);
        const totalGames = Object.values(dayCounts).reduce((a, b) => a + b, 0);
        return { grid, maxGames, totalGames };
    }, []);

    return (
        <div className="calendar-container">
            <div className="calendar-header">
                <span className="calendar-title">{totalGames} games played in the last year</span>
            </div>
            <div className="calendar-graph">
                <div className="calendar-months">
                    {months.map((m, i) => (
                        <span key={i} className="calendar-month">{m}</span>
                    ))}
                </div>
                <div className="calendar-grid">
                    {/* Day labels, aligned with rows */}
                    <div className="calendar-days">
                        {weekdayLabels.map((label, i) => (
                            <span key={i} className={label ? "calendar-day-label" : "calendar-day-label-empty"}>{label}</span>
                        ))}
                    </div>
                    <div className="calendar-weeks">
                        {grid.map((week, wi) => (
                            <div key={wi} className="calendar-week">
                                {week.map((count, di) => (
                                    <div
                                        key={di}
                                        className="calendar-day"
                                        style={{ background: levels[getLevel(count, maxGames)] }}
                                        title={`Games: ${count}`}
                                    ></div>
                                ))}
                            </div>
                        ))}
                    </div>
                </div>
            </div>
            <div className="calendar-footer">
                <div className="calendar-legend">
                    <span>Less</span>
                    {levels.map((color, i) => (
                        <span
                            key={i}
                            className="calendar-legend-square"
                            style={{ background: color }}
                        ></span>
                    ))}
                    <span>More</span>
                </div>
            </div>
        </div>
    );
}
